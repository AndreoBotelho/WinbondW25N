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


spi= SPI(1, baudrate=60000000)

cs = Pin('D5', Pin.OUT, value=1)


def start(point = "/flash2", bs = 512, fmt = False, st = 0, sz = 2048, db = False, clear = False, LFS = False):
    
    dev = W25N(spi,cs)
    
    if dev == None:
        print("coundnt find spi nand device")
        return
    
    flash=NandBdev(dev, blocksize = 512, start = st, size = sz, debug = db)
    
    if flash == None:
        print("error creating block device")
        return
    
    read=64
    prog=512
    look=512
    
    vfs = None
        
    try:
        if clear:
            dev.bulkErase()
        if fmt:
            if LFS:
                os.VfsLfs2.mkfs(flash, readsize=read, progsize=prog, lookahead=look)
            else:
                os.VfsFat.mkfs(flash)
        if LFS:
            vfs = os.VfsLfs2(flash, readsize=read, progsize=prog, lookahead=look)
        else:
            vfs = os.VfsFat(flash)
    except OSError as e:
        print("Mount failed with error", e)
        
    os.mount(vfs, point)
        
    print("block count = {} block size = {} flash size {:1}MB".format(flash.ioctl(4, 0),flash.ioctl(5, 0),flash.ioctl(4, 0)*flash.ioctl(5, 0)/1048576))

        
