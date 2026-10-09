"""Тесты этапа 1: разбор команды и обработка ошибок REPL."""

import os
import sys
import unittest

from emulator import parse_line, execute, cmd_exit, CommandError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class ParseLineTests(unittest.TestCase):
    """Проверка разбора строки ввода в команду и аргументы."""

    def test_splits_command_and_args(self):
        """Команда и аргументы разбираются по пробелам."""
        command, args = parse_line("ls -la /home")
        self.assertEqual(command, "ls")
        self.assertEqual(args, ["-la", "/home"])

    def test_supports_quoted_arguments(self):
        """Аргумент в кавычках остаётся одним токеном."""
        command, args = parse_line('echo "hello world"')
        self.assertEqual(command, "echo")
        self.assertEqual(args, ["hello world"])

    def test_expands_environment_variables(self):
        """$VAR раскрывается значением реальной ОС."""
        os.environ["TEST_VFS_VAR"] = "/tmp/example"
        _, args = parse_line("cd $TEST_VFS_VAR")
        self.assertEqual(args, ["/tmp/example"])

    def test_empty_line_returns_none(self):
        """Пустая строка не считается командой."""
        command, _ = parse_line("   ")
        self.assertIsNone(command)

    def test_unterminated_quote_raises_value_error(self):
        """Незакрытая кавычка — ошибка синтаксиса ввода."""
        with self.assertRaises(ValueError):
            parse_line('ls "unterminated')


class ExecuteTests(unittest.TestCase):
    """Проверка выполнения команд и реакции на ошибки."""

    def test_unknown_command_does_not_raise(self):
        """Неизвестная команда сообщается, но не роняет программу."""
        execute(None, "unknowncmd", ["a", "b"])

    def test_exit_without_args_raises_system_exit(self):
        """exit без аргументов завершает работу."""
        with self.assertRaises(SystemExit):
            cmd_exit(None, [])

    def test_exit_with_args_raises_command_error(self):
        """exit с аргументами — ошибка «неверные аргументы»."""
        with self.assertRaises(CommandError):
            cmd_exit(None, ["extra"])


if __name__ == "__main__":
    unittest.main()
