#!/bin/bash

echo "mony" | sudo -S busybox devmem 0x70003248 32 0x46
sudo busybox devmem 0x6000d100 32 0x00
sudo busybox devmem 0x700031fc 32 0x45
sudo busybox devmem 0x6000d504 32 0x2
cd ~/Desktop/Final_project_08_11/Dove_Chaser
./main.py
