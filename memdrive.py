# The MIT License (MIT)
#
# Copyright (c) 2024 Andre Botelho
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

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


os.mount(vfs, "/flash2")
os.chdir("/flash2")
