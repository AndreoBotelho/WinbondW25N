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

from pyb import Timer

class NandBdev:
    def __init__(self,flash, pagesize = 256, sectorsize = 512, start = 0, debug = False):
        self.debug = debug
        self.flash = flash
        self.f_start = start
        self.write_count = 0
        self.pagesize = pagesize
        self.sectorsize = sectorsize
        self.sectorpages = sectorsize // pagesize
        self.f_sectorsize =  flash.sector_size()
        self.blockcount = self.f_sectorsize // sectorsize
        self.f_pagesize = flash.page_size()
        self.f_size = flash.flash_size()
        self.f_sectorpages =  self.f_sectorsize // self.f_pagesize
        self.pagerel = self.blockcount // self.f_sectorpages
        self.bl_arr = bytearray(self.f_sectorsize)
        self.bl_mem = memoryview(self.bl_arr)
        self.curr_sector = 0
        self.readfsector(0)

    def readblocks(self, n, buf, offset = 0):
        lenght = len(buf)
        f_page = n // self.pagerel
        f_offset = ((n % self.pagerel) * self.sectorsize) + offset
        f_sector = n // self.blockcount
        
        if f_sector == self.curr_sector:
            bl = n % self.blockcount
            mv = self.bl_mem
            for i in range(lenght):
                buf[i] = mv[bl * self.sectorsize + offset + i]
        else:
            self.flash.pageDataRead(f_page)
            self.flash.read(f_offset, buf = buf)
        if self.debug:
            address = (n * self.sectorsize) + offset
            print("read {} at {} sector {} block {} foffset {}".format(lenght,address,f_sector,n,offset))

            

    def writeblocks(self, n, buf, offset = 0):
        f_sector = n // self.blockcount
        if f_sector != self.curr_sector:
            self.refreshcache(f_sector)
        lenght = len(buf)
        bl = n % self.blockcount
        mv = self.bl_mem
        for i in range(lenght):
            mv[bl * self.sectorsize + offset + i] = buf[i]
        self.write_count += 1
        if self.debug:
            address = (n * self.sectorsize) + offset
            print("write {} at {} sector {} block {} offset {}".format(lenght,address,f_sector,n,offset))
        
            
    def readfsector(self, sector):
        page = sector * self.f_sectorpages
        mv = self.bl_mem
        for i in range(64):
            index = i * 2048
            self.flash.pageDataRead(page + i)
            self.flash.read(0, mv[index:index + 2048])
        self.curr_sector = sector
        if self.debug:
            print("load sector ",sector)
        
    def writefsector(self, sector):
        sec_addr = sector * self.f_sectorpages
        self.flash.blockErase(sec_addr)
        mv = self.bl_mem
        for i in range(64):
            index = i * 2048
            self.flash.loadRandProgData(0, mv[index:index + 2048], 2048)
            self.flash.ProgramExecute(sec_addr + i)
        if self.debug:
            print("write sector ",sector)
            
    def refreshcache(self, sector):
        self.writefsector(self.curr_sector)
        self.readfsector(sector)


    def ioctl(self, op, arg):
        if op == 4:  # MP_BLOCKDEV_IOCTL_BLOCK_COUNT
            return  self.f_size // self.sectorsize
        if op == 5:  # MP_BLOCKDEV_IOCTL_BLOCK_SIZE
            return self.sectorsize
        if op == 6:  # MP_BLOCKDEV_IOCTL_BLOCK_ERASE
            n = arg % self.blockcount
            mv = self.bl_mem
            for i in range(self.sectorsize):
                mv[n * self.sectorsize + i] = 0
            if self.debug:
                print("delete block {} ".format(arg))
            return 0
        if op == 3:
            self.writefsector(self.curr_sector)
            if self.debug:
                print("sync")
            return 0

