#!/bin/bash
# Запуск со всеми тремя параметрами одновременно, включая
# выполнение стартового скрипта.
cd "$(dirname "0$")/../scr"
python3 emulator.py \
  --vfs-path /tmp/myshell_vfs.json \
  --promt "full-demo:/$ " \
  --script ../examples/stage2_demo.txt < /dev/null