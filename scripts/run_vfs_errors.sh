#!/bin/bash
# Демонстрация ошибок загрузки VFS: файл не найден, невалидный JSON,
# неверная схема.
cd "$(dirname "$0")/.."
echo "--- файл не найден ---"
printf "exit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/does_not_exist.json
echo
echo "--- некорректный JSON ---"
printf "exit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/malformed.json
echo
echo "--- некорректная схема VFS ---"
printf "exit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/bad_schema.json