# Micropython WinbondW25N NAND Flash soft driver
Arduino Winbond W25N library for use with W25N01GV 1Gb and W25M02GV SPI NAND Flash.

Adapted to micropython for usage as fat filesystem drive, requires 128k buffer to use as cache.

usage in testnand file

````
MPY: sync filesystems
MPY: soft reboot
Nand Flash W25N02GV found
block count = 327680 block size = 512 flash size 160MB
saved 2626.29Kb in 15.23s : 172.442Kb/s
read 2626.29Kb in 1.293s : 2031.16Kb/s
````
