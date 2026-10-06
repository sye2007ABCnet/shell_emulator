"""Тесты этапа 3: загрузка и навигация по VFS."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from vfs import VFS, VFSError, VFSRuntimeError

DEEP_VFS = {
    "name": "root",
    "type": "dir",
    "children": [
        {"name": "top.txt", "type": "file", "content": "0YLQvtC/"},
        {
            "name": "level1",
            "type": "dir",
            "children": [
                {"name": "l1.txt", "type": "file", "content": "MQ=="},
                {
                    "name": "level2",
                    "type": "dir",
                    "children": [
                        {"name": "l2.txt", "type": "file", "content": "Mg=="},
                    ],
                },
            ],
        },
    ],
}


def _write_temp_vfs(data):
    """Сохраняет словарь как временный JSON-файл VFS и возвращает путь."""
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    json.dump(data, handle)
    handle.close()
    return handle.name


def _write_temp_text(text):
    """Сохраняет произвольный текст во временный файл и возвращает путь."""
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    handle.write(text)
    handle.close()
    return handle.name


class VFSLoadTests(unittest.TestCase):
    """Загрузка VFS из JSON-файла и обработка ошибок загрузки."""

    def test_loads_valid_tree(self):
        """Корректный JSON успешно превращается в дерево VFS."""
        path = _write_temp_vfs(DEEP_VFS)
        try:
            vfs = VFS.load(path)
        finally:
            os.remove(path)
        self.assertTrue(vfs.root.is_dir)
        self.assertIn("top.txt", vfs.root.children)

    def test_missing_file_raises_vfs_error(self):
        """Отсутствующий файл VFS - VFSError."""
        with self.assertRaises(VFSError):
            VFS.load("/no/such/vfs.json")

    def test_malformed_json_raises_vfs_error(self):
        """При некоррекнтом JSON выдаёт VFSError."""
        path = _write_temp_text('{ "name": "broken", "type": "dir" ')
        try:
            with self.assertRaises(VFSError):
                VFS.load(path)
        finally:
            os.remove(path)

    def test_missing_type_field_raises_vfs_error(self):
        """Отсутствие поля 'type' — ошибка схемы VFS."""
        path = _write_temp_vfs({"name": "broken", "children": []})
        try:
            with self.assertRaises(VFSError):
                VFS.load(path)
        finally:
            os.remove(path)


class VFSNavigationTests(unittest.TestCase):
    """Навигация по уже загруженной VFS: cd, ls, cat."""

    def setUp(self):
        """Загружает тестовое дерево перед каждым тестом."""
        self.path = _write_temp_vfs(DEEP_VFS)
        self.vfs = VFS.load(self.path)

    def tearDown(self):
        """Удаляет временный файл после теста."""
        os.remove(self.path)

    def test_starts_at_root(self):
        """После загрузки текущая директория - корень."""
        self.assertEqual(self.vfs.cwd_path(), "/")

    def test_change_dir_relative(self):
        """cd по относительному пути меняет текущую директорию."""
        self.vfs.change_dir("level1/level2")
        self.assertEqual(self.vfs.cwd_path(), "/level1/level2")

    def test_change_dir_to_missing_path_raises(self):
        """cd в несуществующий путь - VFSRuntimeError."""
        with self.assertRaises(VFSRuntimeError):
            self.vfs.change_dir("nope")

    def test_change_dir_into_file_raises(self):
        """cd в файл (не в директорию) - VFSRuntimeError."""
        with self.assertRaises(VFSRuntimeError):
            self.vfs.change_dir("top.txt")

    def test_list_dir_root(self):
        """ls в корне показывает top.txt и level1."""
        names = {name for name, _ in self.vfs.list_dir()}
        self.assertEqual(names, {"top.txt", "level1"})

    def test_read_file_returns_bytes(self):
        """cat возвращает декодированное из base64 содержимое."""
        content = self.vfs.read_file("level1/l1.txt")
        self.assertEqual(content, b"1")

    def test_read_dir_as_file_raises(self):
        """cat на директорию - VFSRuntimeError."""
        with self.assertRaises(VFSRuntimeError):
            self.vfs.read_file("level1")


if __name__ == "__main__":
    unittest.main()


