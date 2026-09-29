import os
import shlex
import sys

VFS_NAME = "vfs"

class CommandError(Exception):
    """Ошибка выполнения команды: неверные аргументы и т.п."""

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

def cmd_ls(args):
    """Заглушка: выводит своё имя и полученные аргументы."""
    print(f"ls: аргументы={args}")

def cmd_cd(args):
    """Заглушка: выводит своё имя и полученные аргументы."""
    print(f"cd: аргументы={args}")

def cmd_exit(args):
    """Завершает работу эмулятора. Аргументов не принимает."""
    if args:
        raise CommandError("exit: команда не принимает аргументов")
    raise SystemExit(0)

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

def execute(command, args):
    """Выполняет команду. Печатает сообщение об ошибке, если что-то пошло не так."""
    handler = COMMANDS.get(command)
    if handler is None:
        print(f"{command}: команда не найдена", file=sys.stderr)
        return
    try:
        handler(args)
    except CommandError as exc:
        print(f"ошибка: {exc}", file=sys.stderr)

def prompt() -> str:
    """Формирует приглашение к вводу. Содержит имя VFS."""
    return f"{VFS_NAME}> "

def repl():
    """Основной цикл REPL: читать строку -> разобрать -> выполнить -> печатать."""
    print(f"Эмулятор командной строки. VFS: {VFS_NAME}")
    print("Введите 'exit' для выхода.\n")

    while True:
        try:
            line = input(prompt())
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
            command, args = parse_line(line)
        except ValueError as exc:
            print(f"ошибка разбора команды: {exc}", file=sys.stderr)
            continue

        if command is None:
            continue

        try:
            execute(command, args)
        except SystemExit:
            break

if __name__ == "__main__":
    repl()



