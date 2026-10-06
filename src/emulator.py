import os
import shlex
import sys

from config import parse_args
from vfs import VFS, VFSError

COMMENT_PREFIX = "#"


class CommandError(Exception):
    """Ошибка выполнения команды: неверные аргументы и т.п."""


class ScriptError(Exception):
    """Ошибка стартового скрипта."""


def expand_env_vars(token: str) -> str:
    """Раскрывает переменные окружения реальной ОС вида $HOME, ${HOME}."""
    return os.path.expandvars(token)


def parse_line(line: str):
    """
    Разбирает строку ввода на имя команды и список аргументов.

    Поддерживает кавычки (как в обычном шелле) и раскрытие $VAR в каждом токене.

    Возвращает (None, []) для пустой строки.
    Бросает ValueError при некорректном синтаксисе (например, незакрытая кавычка).
    """
    tokens = shlex.split(line, comments=False, posix=True)
    tokens = [expand_env_vars(t) for t in tokens]
    if not tokens:
        return None, []
    return tokens[0], tokens[1:]


def cmd_ls(vfs, args):
    """Заглушка: выводит своё имя и полученные аргументы."""
    print(f"ls: аргументы={args}")


def cmd_cd(vfs, args):
    """Заглушка: выводит своё имя и полученные аргументы."""
    print(f"cd: аргументы={args}")


def cmd_exit(vfs, args):
    """Завершает работу эмулятора. Аргументов не принимает."""
    if args:
        raise CommandError("exit: команда не принимает аргументов")
    raise SystemExit(0)


def load_vfs(cfg):
    """Загружает VFS согласно конфигурации.

    Если путь не задан - возвращает пустую VFS. Если загрузка не
    удалась - сообщает об ошибке и тоже возвращает пустую VFS, чтобы
    эмулятор мог продолжить работу, а не падать целиком.
    """
    if not cfg.vfs_path:
        return VFS.empty(cfg.vfs_name)
    try:
        return VFS.load(cfg.vfs_path)
    except VFSError as exc:
        print(f"ошибка загрузки VFS: {exc}", file=sys.stderr)
        return VFS.empty(cfg.vfs_name)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute(vfs, command, args):
    """Выполняет команду. Печатает сообщение об ошибке, если что-то пошло не так."""
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"{command}: команда не найдена", file=sys.stderr)
        return
    try:
        handler(vfs, args)
    except CommandError as exc:
        print(f"ошибка: {exc}", file=sys.stderr)


def run_line(vfs, line, echo_prompt=None):
    """Разбирает и выполняет одну строку команды.

    Если echo_prompt задан, печатает "приглашение+команда" перед
    выполнением - имитация ввода пользователем (нужно для скрипта).
    """
    if echo_prompt is not None:
        print(f"{echo_prompt}{line}")
    try:
        command, args = parse_line(line)
    except ValueError as exc:
        print(f"ошибка разбора команды: {exc}", file=sys.stderr)
        return
    if command is not None:
        execute(vfs, command, args)


def load_script_lines(path):
    """Читает строки стартового скрипта, пропуская пустые строки
    и комментарии (начинающиеся с '#').

    Возвращает список пар (номер строки, текст команды).
    Бросает ScriptError, если файл не удалось открыть.
    """
    try:
        with open(path, "r") as script_file:
            raw_lines = script_file.readlines()
    except OSError as exc:
        raise ScriptError(f"не удалось открыть '{path}': {exc}") from exc

    result = []
    for lineno, raw in enumerate(raw_lines, 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX):
            continue
        result.append((lineno, raw.rstrip("\n")))
    return result


def run_script(vfs, path, prompt_text):
    """Выполняет стартовый скрипт, имитируя диалог с пользователем.

    Ошибка в отдельной строке скрипта сообщается (с номером строки),
    но не прерывает выпролнение остальных строк.
    """
    try:
        lines = load_script_lines(path)
    except ScriptError as exc:
        print(f"ошибка стартового скрипта: {exc}", file=sys.stderr)
        return

    for lineno, line in lines:
        try:
            run_line(vfs, line, echo_prompt=prompt_text)
        except SystemExit:
            raise
        except Exception as exc:
            print(
                f"ошибка стартового скрипта (строка {lineno}): {exc}",
                file=sys.stderr,
            )


def repl(vfs, prompt_text):
    """Основной интерактивный цикл REPL."""
    while True:
        try:
            line = input(prompt_text)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print()
            continue

        line = line.strip()
        if not line:
            continue

        try:
            run_line(vfs, line)
        except SystemExit:
            break


def main(argv=None):
    """Точка входа: читает конфигурацию, выполняет скрипт, запускает REPL."""
    cfg = parse_args(argv)
    print(cfg.describe())
    print()

    vfs = load_vfs(cfg)

    print(f"Эмулятор командной строки. VFS: {cfg.vfs_name}")
    print("Введите 'exit' для выхода.\n")

    if cfg.script:
        try:
            run_script(vfs, cfg.script, cfg.prompt)
        except SystemExit:
            return

    try:
        repl(vfs, cfg.prompt)
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
