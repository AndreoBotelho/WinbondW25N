import os
from nandbdev import NandBdev
from nandflash import W25N
from machine import SPI, Pin,SoftSPI


spi= SPI(1, baudrate=40000000)

cs = Pin('D5', Pin.OUT, value=1)

dev = W25N(spi,cs)

#dev = SPIflash(spi, cs)
#dev.bulkErase()

flash=NandBdev(dev, sectorsize = 512, debug = False)

print("block_count = {} block_size = {} ".format(flash.ioctl(4, 0),flash.ioctl(5, 0)))

# try:
#     vfs = os.VfsFat(flash)
# except OSError as e:
#     print("Mount failed with error", e)
#     print("Recreate the file system")

read=128
prog=512
look=2048


os.VfsFat.mkfs(flash)#, readsize=read, progsize=prog, lookahead=look)
vfs = os.VfsFat(flash)#,readsize=read, progsize=prog, lookahead=look)
#print(dev.flash_size())

#print("open fs")

os.mount(vfs, "/flash2")
os.chdir("/flash2")
