#!/bin/bash
# Загрузка VFS с глубиной вложенности от 3 уровней.
cd "$(dirname "$0")/.."
printf "ls\nexit\n" | python3 src/emulator.py --vfs-path fixtures/vfs/deep_structure.json