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

import nanddrive as nand
import os
import time
from pyb import Timer
import shutil


nand.start(db = False, fmt = False, st = 256, sz = 1280, clear = False, LFS = False)

sourcename = '/flash2/ST77_STM320.zip'
destname = '/flash/BMI/ST77_STM32{}.zip'

src = open(sourcename,'r')
filesize = os.stat(sourcename)
filesize = filesize[6]

samples = 3

start = time.ticks_ms()

for i in range(samples):
    src.seek(0)
    dst = open(destname.format(i),'w')
    shutil.copyfileobj(src,dst,length=2048)
    dst.close()

    
elapsed = time.ticks_diff(time.ticks_ms(),start) / 1000 
transfer = filesize * samples / 1024

print("saved {:02}Kb in {:02}s : {:02}Kb/s".format(transfer, elapsed, transfer/elapsed))


block = os.statvfs("/flash2")[0]
buf = bytearray(4096)
mv = memoryview(buf)

start = time.ticks_ms()

for i in range(samples):
    dst = open(destname.format(i),'r')
    for i in range(filesize // len(mv)):
        dst.readinto(mv)
    dst.close()

    
elapsed = time.ticks_diff(time.ticks_ms(),start) / 1000
transfer = filesize * samples / 1024

print("read {:02}Kb in {:02}s : {:02}Kb/s".format(transfer, elapsed, transfer/elapsed))
    
