"""
Этап 3: виртуальная файловая система (VFS).

VFS целиком хранится в памяти. Источником данных является JSON-файл;
содержимое файлов кодируется в base64 (подходит и для текста, и для
двоичных данных). Исходный JSON-файл никогда не изменяется и не
распаковывается на диск — любые последующие модификации (этапы 4-5)
происходят только в памяти процесса.
"""

import base64
import json

DEFAULT_DIR_PERMISSIONS = "rwxr-xr-x"
DEFAULT_FILE_PERMISSIONS = "rw-r--r--"


class VFSError(Exception):
    """Ошибка загрузки VFS: файл не найден, неверный JSON или схема."""


class VFSRuntimeError(Exception):
    """Ошибка работы с VFS во время выполнения команд (путь не
        найден, попытка войти в файл как в директорию и т.п.)."""


class VFSNode:
    """Один узел дерева VFS: файл или директория."""

    __slots__ = ("name", "is_dir", "permissions", "children", "content")

    def __init__(self, name, is_dir, permissions=None, children=None, content=b""):
        self.name = name
        self.is_dir = is_dir
        self.permissions = permissions or (
            DEFAULT_DIR_PERMISSIONS if is_dir else DEFAULT_FILE_PERMISSIONS
        )
        self.children = children if children is not None else (
            {} if is_dir else None
        )
        self.content = content


def _require_name(data, where):
    """Проверяет и возвращает поле 'name' узла."""
    name = data.get("name")
    if not isinstance(name, str) or not name:
        raise VFSError(f"{where}: отсутствует корректное поле 'name'")
    return name


def _require_type(data, where):
    """Проверяет и возвращает поле 'type' узла ('file' или 'dir')."""
    node_type = data.get("type")
    if node_type not in ("file", "dir"):
        raise VFSError(f"{where}: поле 'type' должно быть 'file'/'dir'")
    return node_type


def _decode_content(data, where):
    """Декодирует base64-содержимое файла в bytes."""
    content_b64 = data.get("content", "")
    if not isinstance(content_b64, str):
        raise VFSError(f"{where}: поле 'content' должно быть строкой")
    if not content_b64:
        return b""
    try:
        return base64.b64decode(content_b64, validate=True)
    except (ValueError, ValueError) as exc:
        raise VFSError(f"{where}: некорректные данные base64 ({exc})") from exc


def _build_file_node(data, where, name, permissions):
    """Строит VFSNode для узла типа 'file'."""
    content = _decode_content(data, where)
    return VFSNode(name, is_dir=False, permissions=permissions, content=content)


def _build_dir_node(data, where, name, permissions):
    """Строит VFSNode для узла типа 'dir', рекурсивно обрабатывая
        дочерние узлы."""
    raw_children = data.get("children", [])
    if not isinstance(raw_children, list):
        raise VFSError(f"{where}: поле 'children' должно быть списком")

    node = VFSNode(name, is_dir=True, permissions=permissions, children={})
    for child_data in raw_children:
        child = _build_node(child_data, where)
        if child.name in node.children:
            raise VFSError(f"{where}: повторяющееся имя '{child.name}'")
        node.children[child.name] = child
    return node


def _build_node(data, parent_path):
    """Рекурсивно строит VFSNode из уже распарсенного JSON-объекта."""
    if not isinstance(data, dict):
        raise VFSError(f"{parent_path or '/'}: узел должен быть объектом")

    name = _require_name(data, parent_path or "/")
    where = f"{parent_path}/{name}"
    node_type = _require_type(data, where)

    permissions = data.get("permissions")
    if permissions is not None and not isinstance(permissions, str):
        raise VFSError(f"{where}: поле 'permissions' должно быть строкой")

    if node_type == "dir":
        return _build_dir_node(data, where, name, permissions)
    return _build_file_node(data, where, name, permissions)


class VFS:
    """Виртуальная файловая система, целиком хранящаяся в памяти."""

    def __init__(self, root, source_path=None):
        self.root = root
        self.source_path = source_path
        self.cwd_parts = []

    @classmethod
    def load(cls, path):
        """Загружает VFS из JSON-файла. Бросает VFSError при любой проблеме."""
        try:
            with open(path, "r") as vfs_file:
                raw = vfs_file.read()
        except OSError as exc:
            raise VFSError(f"не удалось открыть файл VFS '{path}': {exc}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise VFSError(f"файл VFS '{path}' содержит некорректный JSON: {exc}'") from exc

        root = _build_node(data, "")
        if not root.is_dir:
            raise VFSError("корневой узел VFS должен быть директорией")
        return cls(root, source_path=path)

    @classmethod
    def empty(cls, name="vfs"):
        """Создаёт пустую VFS - для случая, кода путь не задан или
        загрузка не удалась."""
        return cls(VFSNode(name, is_dir=True, children={}))

    def _split_path(self, path):
        """Превращает путь (абсолютный или относительный) в список имён
        от корня с учётом '.', '..' и текущей директории."""
        parts = [] if path.startswith("/") else list(self.cwd_parts)
        for part in path.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(part)
        return parts

    def _node_at(self, parts):
        """Возвращает узел по списку имён от корня."""
        node = self.root
        for depth, part in enumerate(parts):
            if not node.is_dir:
                visited = "/" + "/".join(parts[:depth])
                raise VFSRuntimeError(f"{visited}: не найдено")
            child = node.children.get(part)
            if child is None:
                full = "/" + "/".join(parts)
                raise VFSRuntimeError(f"{full}: не найдено")
            node = child
        return node

    def resolve(self, path):
        """Возвращает VFSNode по пути (абсолютному или относительному)."""
        return self._node_at(self._split_path(path))

    def cwd_path(self):
        """Текущая директория в виде абсолютного пути."""
        return "/" + "/".join(self.cwd_parts)

    def change_dir(self, path):
        """Меняет текущую директорию. Бросает VFSRuntimeError, если путь
        не найден или указывает на файл."""
        parts = self._split_path(path)
        node = self._node_at(parts)
        if not node.is_dir:
            raise VFSRuntimeError(f"{path}: не является директорией")
        self.cwd_parts = parts

    def list_dir(self, path=None):
        """Список (имя, это директория?) для указанной или текущей
        директории. Для файла возвращает список из одного элемента."""
        node = self.resolve(path) if path else self._node_at(self.cwd_parts)
        if not node.is_dir:
            return [(node.name, False)]
        entries = ((c.name, c.is_dir) for c in node.children.values())
        return sorted(entries, key=lambda entry: (not entry[1], entry[0]))

    def read_file(self, path):
        """Возвращает содержимое файла. Бросает VFSRuntimeError, если
        путь - директория или не найден."""
        node = self.resolve(path)
        if node.is_dir:
            raise VFSRuntimeError(f"{path}: это директория")
        return node.content


