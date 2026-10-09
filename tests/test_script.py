"""Тесты этапа 2: загрузка и выполнение стартового скрипта."""

import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

from emulator import load_script_lines, run_script, ScriptError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _write_temp_script(text):
    """Создаёт временный файл со скриптом и возвращает путь к нему."""
    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8",
    )
    handle.write(text)
    handle.close()
    return handle.name


class LoadScriptLinesTests(unittest.TestCase):
    """Разбор файла стартового скрипта."""

    def test_skips_blank_and_comments(self):
        """Пустые строки и строки-комментарии пропускаются."""
        path = _write_temp_script("# комментарий\n\nls -la\n")
        try:
            lines = load_script_lines(path)
        finally:
            os.remove(path)
        self.assertEqual(lines, [(3, "ls -la")])

    def test_missing_file_raises_script_error(self):
        """Отсутствующий файл скрипта - ScriptError."""
        with self.assertRaises(ScriptError):
            load_script_lines("/no/such/file.txt")


class RunScriptTests(unittest.TestCase):
    """Выполнение стартового скрипта целиком."""

    def test_echoes_prompt_and_command(self):
        """На экран выводится приглашение+команда и результат."""
        path = _write_temp_script("ls -la\n")
        buf = StringIO()
        try:
            with redirect_stdout(buf):
                run_script(None, path, "vfs> ")
        finally:
            os.remove(path)
        output = buf.getvalue()
        self.assertIn("vfs> ls -la", output)
        self.assertIn("ls: аргументы=['-la']", output)

    def test_continues_after_error_in_script(self):
        """Ошибка в одной строке не прерывает выполнение остальных."""
        path = _write_temp_script("badcmd\nls\n")
        buf = StringIO()
        try:
            with redirect_stdout(buf):
                run_script(None, path, "vfs> ")
        finally:
            os.remove(path)
        self.assertIn("vfs> ls", buf.getvalue())


if __name__ == '__main__':
    unittest.main()
