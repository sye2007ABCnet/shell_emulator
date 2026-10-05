"""Тесты этапа 2: разбор параметров командной строки и Config."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import Config, parse_args


class ConfigDefaultTests(unittest.TestCase):
    """Поведение Config без явных параметров."""

    def test_default_vfs_name_is_vfs(self):
        """Без --vfs-path имя VFS равно 'vfs'."""
        cfg = Config()
        self.assertEqual(cfg.vfs_name, 'vfs')

    def test_default_prompt_contains_vfs_name(self):
        """Приглашение по умолчанию содержит имя VFS."""
        cfg = Config()
        self.assertIn(cfg.vfs_name, cfg.prompt)


class ConfigVfsNameTests(unittest.TestCase):
    """Вычисление имени VFS из пути к файлу."""
    def test_vfs_name_from_path(self):
        """Имя VFS - это базовое имя файла без расширения."""
        cfg = Config(vfs_path="/data/my_vfs.json")
        self.assertEqual(cfg.vfs_name, "my_vfs")

    def test_vfs_name_without_extension(self):
        """Путь без расширения тоже даёт корректное имя."""
        cfg = Config(vfs_path="/data/myvfs")
        self.assertEqual(cfg.vfs_name, "myvfs")


class ConfigPromptTests(unittest.TestCase):
    """Переопределение приглашения пользователем."""

    def test_custom_prompt_gets_trailing_space(self):
        """К приглашению без пробела в конце пробел добавляется."""
        cfg = Config(prompt="myshell:~$")
        self.assertTrue(cfg.prompt.endswith(" "))


class ParseArgsTests(unittest.TestCase):
    """Разбор аргументов командной строки целиком."""

    def test_parses_all_three_parameters(self):
        """Все три параметра командной строки распознаются."""
        cfg = parse_args([
            "--vfs-path", "/tmp/example.json",
            "--prompt", "demo> ",
            "--script", "/tmp/example.txt"
        ])
        self.assertEqual(cfg.vfs_path, "/tmp/example.json")
        self.assertEqual(cfg.prompt, "demo> ")
        self.assertEqual(cfg.script, "/tmp/example.txt")

    def test_no_parameters_gives_defaults(self):
        """Без параметров используются значения по умолчанию."""
        cfg = parse_args([])
        self.assertIsNone(cfg.vfs_path)
        self.assertIsNone(cfg.script)


if __name__ == '__main__':
    unittest.main()
