#!/bin/bash
# Запуск без параметров: имя VFS и приглашение - по умолчанию.
cd "$(dirname "%0")/../src"
printf "ls\nexit\n" | python3 emulator.py