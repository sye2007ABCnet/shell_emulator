"""
Этап 2: конфигурация эмулятора.

Поддерживаемые параметры командной строки:
    --vfs-path   путь к физическому расположению VFS (JSON-файл)
    --prompt      пользовательское приглашшение к вводу
    --script     путь к стартовому скрипту
"""

import argparse
import os


class Config:
    """Хранит парамкетры запуска эмулятора и производные значения."""

    def __init__(self, vfs_path=None, prompt=None, script=None):
        self.vfs_path = vfs_path
        self.script = script
        self.vfs_name = self._compute_vfs_name(vfs_path)
        self.prompt = self._compute_prompt(prompt, self.vfs_name)

    @staticmethod
    def _compute_vfs_name(vfs_path):
        """Имя VFS для приглашения - базовое имя файла без расширения."""
        if not vfs_path:
            return "vfs"
        base = os.path.basename(os.path.normpath(vfs_path))
        name, _ext = os.path.splitext(base)
        return name or "vfs"

    @staticmethod
    def _compute_prompt(prompt, vfs_name):
        """Пользовательское приглашение переопределяет значение по
        умолчанию; по умолчанию приглашение содержит имя VFS."""
        if prompt:
            return prompt if prompt.endswith((" ", "\t")) else prompt + " "
        return f"{vfs_name}> "

    def describe(self):
        """Отладочный вывод всех параметров конфигурации при запуске."""
        vfs_path = self.vfs_path or "(не задан)"
        script = self.script or "(не задан)"
        lines = [
            "Параметры конфигурации эмулятора:",
            f"  путь к VFS       : {vfs_path}",
            f"  имя VFS          : {self.vfs_name}",
            f"  приглашение      : {self.prompt}",
            f"  стартовый скрипт : {script}",
        ]
        return "\n".join(lines)

def parse_args(argv=None):
    """Разбирает аргументы командной строки и возвращает Config."""
    parser = argparse.ArgumentParser(
        prog="emulator.py",
        description="Эмулятор командной строки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs-path", dest="vfs_path", default=None,
        help="путь к физическому расположению VFS (JSON-файл)",
    )
    parser.add_argument(
        "--prompt", dest="prompt", default=None,
        help="пользовательчкое приглашение к вводу",
    )
    parser.add_argument(
        "--script", dest="script", default=None,
        help="путь к стартовому скрипту",
    )
    namespace = parser.parse_args(argv)
    return Config(
        vfs_path=namespace.vfs_path,
        prompt=namespace.prompt,
        script=namespace.script,
    )


