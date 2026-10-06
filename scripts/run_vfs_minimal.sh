#!/bin/bash
# Загрузка минимальной VFS (один файл в корне).
cd "$(dirname "$0")/.."
printf "ls\nexit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/minimal.json