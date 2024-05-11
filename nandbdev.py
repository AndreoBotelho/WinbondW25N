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
    def __init__(self,flash, blocksize = 512, start = 0, size = 0, debug = False):
        self.debug = debug
        self.flash = flash
        self.write_count = 0
        self.blocksize = blocksize
        self.f_sectorsize =  flash.sector_Size()
        self.f_start = start * self.f_sectorsize // blocksize
        self.blockcount = self.f_sectorsize // blocksize
        self.f_pagesize = flash.page_Size()
        if size == 0:
            self.f_size = flash.flash_Size() - start * self.f_sectorsize
        else:
            self.f_size = size * self.f_sectorsize
        self.f_sectorpages =  self.f_sectorsize // self.f_pagesize
        self.pagerel = self.blockcount // self.f_sectorpages
        self.bl_arr = bytearray(self.f_sectorsize)
        self.bl_mem = memoryview(self.bl_arr)
        self.pg_arr = bytearray(self.f_pagesize)
        self.pg_mem = memoryview(self.pg_arr)
        self.curr_sector = start
        self.curr_page = -1
        self.readfsector(start)
        

    def readblocks(self, n, buf, offset = 0):
        buf = memoryview(buf)
        n +=  self.f_start
        bs = self.blocksize
        lenght = len(buf)
        index = 0
        
        if self.debug:
            f_sector = n // self.blockcount
            address = (n * bs) + offset
            print("read {} at {} sector {} block {} offset {}".format(lenght,address,f_sector,n,offset))
        
        #####################    read page   #################################
        if 0:#lenght >= self.f_pagesize:
            bs = self.f_pagesize
            while lenght >= bs:
                pbuf = buf[index:index + bs - offset]
                f_sector = n // self.blockcount
                if f_sector == self.curr_sector:
                    addr = (n % self.blockcount) * self.blocksize
                    if addr + offset > self.f_sectorsize - self.f_pagesize:
                        print("read page overflow")
                        break
                    mv = self.bl_mem
                    pbuf[:] = mv[addr + offset:addr + bs]
                else:
                    f_page, f_offset = (n // self.pagerel, n % self.pagerel)
                    f_offset = (f_offset * self.blocksize) + offset
                    self.flash.pageDataRead(f_page)
                    self.flash.read(f_offset, buffer =  pbuf)
                index += (bs - offset)
                n += self.f_pagesize // self.blocksize
                lenght -= (bs - offset)
                offset = 0
        ###################    read block   ################################
        if lenght >= self.blocksize:
            bs = self.blocksize
            while lenght >= bs:
                pbuf = buf[index:index + bs- offset]
                f_sector = n // self.blockcount
                if f_sector == self.curr_sector:
                    addr =  (n % self.blockcount) * bs 
                    mv = self.bl_mem
                    pbuf[:] = mv[addr + offset:addr + bs]
                else:
                    f_page, f_offset = (n // self.pagerel, n % self.pagerel)
                    f_offset = (f_offset * bs) + offset
                    if f_page != self.curr_page:
                        self.flash.pageDataRead(f_page)
                        self.flash.read(0, self.pg_mem)
                        self.curr_page = f_page
                    mv = self.pg_mem
                    pbuf[:] = mv[f_offset:f_offset+ bs]
                index += (bs - offset)
                n += 1
                lenght -= (bs - offset)
                offset = 0
            
        #####################  read bytes ################################   
        if lenght > 0:
            pbuf = buf[index:]
            f_sector, addr = (n // self.blockcount, n % self.blockcount)
            addr *= bs
            if f_sector == self.curr_sector:
                mv = self.bl_mem
                pbuf[:] = mv[addr + offset: addr + offset + lenght]
            else:
                f_page, f_offset = (n // self.pagerel, n % self.pagerel)
                f_offset = (f_offset * bs) + offset
                if f_page != self.curr_page:
                    self.flash.pageDataRead(f_page)
                    self.flash.read(0, self.pg_mem)
                    self.curr_page = f_page
                mv = self.pg_mem
                pbuf[:] = mv[f_offset:f_offset+ lenght]

            
    def writeblocks(self, n, buf, offset = 0):
        n = n + self.f_start
        lenght = len(buf)
        f_sector = n // self.blockcount
        if f_sector != self.curr_sector:
            self.refreshcache(f_sector)
        lenght = len(buf)
        bl = n % self.blockcount
        mv = self.bl_mem
        if self.debug:
            address = (n * self.blocksize) + offset
            print("write {} at {} sector {} block {} offset {}".format(lenght,address,f_sector,n,offset))
        addr = bl * self.blocksize
        rest = 0
        if (addr + offset + lenght) > self.f_sectorsize:
            rest = lenght
            lenght = self.f_sectorsize - addr
            rest = rest - lenght
            if self.debug:
                print("overflow {} bytes addr {} sector{}".format(rest,addr,f_sector))
        index = 0
        mv[addr + offset:addr + offset + lenght] = buf[:lenght]
        if rest > 0:
            self.refreshcache(f_sector + 1)
            mv[:rest] = buf[lenght:]
        self.write_count += 1

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
        self.curr_page = -1


    def ioctl(self, op, arg):
        if op == 4:  # MP_BLOCKDEV_IOCTL_BLOCK_COUNT
            return  self.f_size // self.blocksize
        if op == 5:  # MP_BLOCKDEV_IOCTL_BLOCK_SIZE
            return  self.blocksize
        if op == 6:  # MP_BLOCKDEV_IOCTL_BLOCK_ERASE
            if self.debug:
                print("delete block {} ".format(arg))
            return 0
        if op == 3:
            self.writefsector(self.curr_sector)
            if self.debug:
                print("sync")
            return 0

