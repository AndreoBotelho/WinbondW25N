# The MIT License (MIT)
#
# Copyright (c) 2022 Robert Hammelrath
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

# /*
#  * Winbond W25N Flash Library
#  * Written by Cameron Houston for UGRacing Formula Student
#  * 09 2019
#  */
# 
# // adapted to mpy by Andre Botelho 2024
# 
# //TODO add support for multi-Gb chips that require bank switching
# //TODO add proper error codes
# //TODO add ECC support functions

import machine
import time
from micropython import const


W25M_DIE_SELECT         = const(0xC2)

W25N_RESET              = const(0xFF)
W25N_JEDEC_ID           = const(0x9F)
W25N_READ_STATUS_REG    = const(0x05)
W25N_WRITE_STATUS_REG   = const(0x01)
W25N_WRITE_ENABLE       = const(0x06)
W25N_WRITE_DISABLE      = const(0x04)
W25N_BB_MANAGE          = const(0xA1)
W25N_READ_BBM           = const(0xA5)
W25N_LAST_ECC_FAIL      = const(0xA9)
W25N_BLOCK_ERASE        = const(0xD8)
W25N_PROG_DATA_LOAD     = const(0x02)
W25N_RAND_PROG_DATA_LOAD= const(0x84)
W25N_PROG_EXECUTE       = const(0x10)
W25N_PAGE_DATA_READ     = const(0x13)
W25N_READ               = const(0x03)
W25N_FAST_READ          = const(0x0B)

W25N_PROT_REG           = const(0xA0)
W25N_CONFIG_REG         = const(0xB0)
W25N_STAT_REG           = const(0xC0)

WINBOND_MAN_ID          = const(0xEF)
W25N01GV_DEV_ID         = const(0xAA21)
W25M02GV_DEV_ID         = const(0xBB22)
W25N02GV_DEV_ID         = const(0xAA22)

W25N01GV_MAX_PAGE       = const(65535)
W25N_MAX_COLUMN         = const(2112)
W25M02GV_MAX_PAGE       = const(131071)
W25M02GV_MAX_DIES       = const(2)
W25N02GV_MAX_PAGE       = const(131071)
W25N02GV_MAX_DIES       = const(1)
W25N_BLOCK_PAGES        = const(64)
W25N_PAGES_SIZE         = const(2048)
W25N_CACHE_SIZE         = const(2176)



class W25N(object):

#   /* initialises the flash and checks that the flash is 
#    * functioning and is the right model.
    def __init__(self, spi, cs):
        self._cs = cs
        self._dieSelect = 1
        self._spi = spi
        self._rdbuf = bytearray(5)
        self.buf_a =  bytearray(5)
        self._buf = memoryview(self.buf_a)
        self._cmdbuf = bytearray(5)
        self._model = None
        self._cs(1)
        self.reset()
        self._buf[0] = W25N_JEDEC_ID
        self._buf[1] = 0x00
        buf = self.sendData(self._buf,2,3)
        if buf[0] == WINBOND_MAN_ID:
            if (buf[1] << 8 | buf[2]) == W25N01GV_DEV_ID:
                self.setStatusReg(W25N_PROT_REG, 0x00)
                self._model = 'W25N01GV'
                print("Nand Flash {} found".format(self._model ))
                self.size = 131072
            if (buf[1] << 8 | buf[2]) == W25M02GV_DEV_ID:
                self._model = 'W25M02GV'
                #self.setStatusReg(W25N_CONFIG_REG,0x9) # disable ECC
                self.dieSelect(0)
                self.setStatusReg(W25N_PROT_REG, 0x00)
                self.dieSelect(1)
                self.setStatusReg(W25N_PROT_REG, 0x00)
                self.dieSelect(0)
                self.size = 262144
                print("Nand Flash {} found".format(self._model ))
            if (buf[1] << 8 | buf[2]) == W25N02GV_DEV_ID:
                self._model = 'W25N02GV'
                #self.setStatusReg(W25N_CONFIG_REG,0x9) # disable ECC
                self.setStatusReg(W25N_PROT_REG, 0x00)
                self.size = W25N_PAGES_SIZE * W25N02GV_MAX_PAGE
                print("Nand Flash {} found".format(self._model ))
        else:
            print("error initializing Nand Flash")
        self.block_size = W25N_BLOCK_PAGES * W25N_PAGES_SIZE

#   /* int dieSelect(uint32_t die) -- Selects the active die on a multi die chip (W25*M*)
#    * Input - die number starting at 0 
#    * Output - error output, 0 for success
            
    def dieSelect(self, die):
        #//TODO add some type of input validation
        self.clearBuf()
        self._buf[0] = W25M_DIE_SELECT
        self._buf[1] = die
        self.sendCmd(self._buf,2)
        self._dieSelect = die

#   /* sendData(buf, len) -- Sends/recieves data to the flash chip.
#    * The buffer that is passed to the function will have its dat sent to the
#    * flash chip, and the data recieved will be returned

def sendData(self, buf, nw, nr = None):
        self._cs(0)
        self._spi.write(buf[:nw])
        if nr:
            self._rdbuf = self._spi.read(nr)
        self._cs(1)
        return self._rdbuf[:nr]
    
    
#   /* sendCmd( cmd, len) -- Sends command to the flash chip.
    
    def sendCmd(self, cmd, len):
        self._cs(0)
        self._spi.write(cmd[:len])
        self._cs(1)
        

#   /* reset() -- resets the device. */
    def reset(self):
        #TODO check WIP in case of reset during write
        self._buf[0] = W25N_RESET
        self.sendCmd(self._buf,1)
        time.sleep_ms(1)
          
#   /* int dieSelectOnAdd(pageAdd) -- auto changes selected die based on requested address
#    * Input - full range (across all dies) page address
#    * Output - error output, 0 for success
    
    def dieSelectOnAdd(self, pageAdd):
        if pageAdd > self.getMaxPage():
            return 1
        if self._model == "W25M02GV":
            return self.dieSelect(pageAdd // W25N01GV_MAX_PAGE)
        else:
            return 0

#   /* getStatusReg(reg) -- gets the value from one of the registers:
#    * W25N_STAT_REG / W25N_CONFIG_REG / W25N_PROT_REG
#    * Output -- register byte value
    
    def getStatusReg(self, reg):
        self.clearBuf()
        self._buf[0] = W25N_READ_STATUS_REG
        self._buf[1] = reg
        buf = self.sendData(self._buf,2,3)
        return buf

#   /* setStatusReg(char reg, char set) -- Sets one of the status registers:
#    * W25N_STAT_REG / W25N_CONFIG_REG / W25N_PROT_REG
#    * set input -- char input to set the reg to */
    
    def setStatusReg(self, reg, _set):
        self.clearBuf()
        self._buf[0] = W25N_WRITE_STATUS_REG
        self._buf[1] = reg
        self._buf[2] = _set
        self.sendCmd(self._buf,3)
        
#   /* getMaxPage() Returns the max page for the given chip

    def getMaxPage(self):
        if self._model == "W25M02GV":
            return W25M02GV_MAX_PAGE
        elif self._model == "W25N01GV":
            return W25N01GV_MAX_PAGE
        elif self._model == "W25N02GV":
            return W25N02GV_MAX_PAGE

#   /* writeEnable() -- enables write opperations on the chip.
#    * Is disabled after a write operation and must be recalled.

    def writeEnable(self):
        self._buf[0] = W25N_WRITE_ENABLE
        self.sendCmd(self._buf,1)

#    /* writeDisable() -- disables all write opperations on the chip */
    
    def writeDisable(self):
        self._buf[0] = W25N_WRITE_DISABLE
        self.sendCmd(self._buf,1)

#   /* blockErase(uint32_t pageAdd) -- Erases one block of data on the flash chip. One block is 64 Pages, and any given 
#   * page address within the block will erase that block.
#   * Rerturns 0 if successful

    def blockErase(self, pageAdd):
        if pageAdd > self.getMaxPage():
            return 1
        self.dieSelectOnAdd(pageAdd)
        #pageAdd = pageAdd // 2048
        cbuf = bytearray(4)
        cbuf[0] = W25N_BLOCK_ERASE
        cbuf[1] = (pageAdd & 0xFF0000) >> 16
        cbuf[2] = (pageAdd & 0xFF00)>> 8
        cbuf[3] = pageAdd & 0xFF
        self.block_WIP()
        self.writeEnable()
        self._cs(0)
        self._spi.write(cbuf)
        self._cs(1)
        return 0
    
#     /* bulkErase() -- Erases the entire chip
#      * THIS TAKES A VERY LONG TIME, ~30 SECONDS
#      * Returns 0 if successful 

    def bulkErase(self):
        error = 0
        sectors = self.getMaxPage() // 64
        for i in range(sectors):
            print("Erasing Sector ",i)
            error = self.blockErase(i*64)
            self.block_WIP()
            if(error != 0):
                return error
        return 0

#   /* loadProgData(columnAdd, buf, dataLen) -- Transfers datalen number of bytes from the 
#    * given buffer to the internal flash buffer (2Kb), to be programed once a ProgramExecute command is sent.
#    * datalLen cannot be more than the internal buffer size of 2111 bytes, or 2048 if ECC is enabled on chip.
#    * When called any data in the internal buffer beforehand will be nullified.
#    * WILL ERASE THE DATA IN BUF OF LENGTH DATALEN BYTES
    
    def loadProgData(self, columnAdd, buf, dataLen, pageAdd = None):
        if columnAdd > W25N_MAX_COLUMN:
            return 1
        if dataLen > W25N_MAX_COLUMN - columnAdd:
            return 1
        if pageAdd:
            if self.dieSelectOnAdd(pageAdd):
                return 1
        cbuf = bytearray(3)
        cbuf[0] = W25N_PROG_DATA_LOAD
        cbuf[1] = (columnAdd & 0xFF00)>> 8
        cbuf[2] = columnAdd & 0xff
        self.block_WIP()
        self.writeEnable()
        self._cs(0)
        self._spi.write(cbuf)
        self._spi.write(buf[:dataLen])
        self._cs(1)
        return 0

#   /* loadRandProgData(columnAdd, buf, dataLen) -- Transfers datalen number of bytes from the 
#    * given buffer to the internal flash buffer, to be programed once a ProgramExecute command is sent.
#    * datalLen cannot be more than the internal buffer size of 2111 bytes, or 2048 if ECC is enabled on chip.
#    * Unlike the normal loadProgData the loadRandProgData function allows multiple transfers (4) to the internal buffer
#    * without the nulling of the currently kept data. 
#    * WILL ERASE THE DATA IN BUF OF LENGTH DATALEN BYTES
    
    def loadRandProgData(self, columnAdd, buf, dataLen, pageAdd = None):
        if columnAdd > W25N_MAX_COLUMN:
            return 1
        if dataLen >  (W25N_MAX_COLUMN - columnAdd):
            return 1
        if pageAdd is not None:
            if self.dieSelectOnAdd(pageAdd):
                return 1
        cbuf = bytearray(3)
        cbuf[0] = W25N_RAND_PROG_DATA_LOAD
        cbuf[1] = (columnAdd & 0xFF00)>> 8
        cbuf[2] = columnAdd & 0xff
        self.block_WIP()
        self.writeEnable()
        self._cs(0)
        self._spi.write(cbuf)
        self._spi.write(buf)
        self._cs(1)
        return 0;

#   /* ProgramExecute(add) -- Commands the flash to program the internal buffer contents to the addres page
#    * given after a loadProgData or loadRandProgData has been called.
#    * The selected page needs to be erased prior to use as the falsh chip can only change 1's to 0's
#    * This command will put the flash in a busy state for a time, so busy checking is required ater use.  */
    def ProgramExecute(self, pageAdd):
        if pageAdd > self.getMaxPage():
            print("execute add out of bounds")
            return 1
        self.dieSelectOnAdd(pageAdd)
        self.writeEnable()
        cbuf = bytearray(4)
        cbuf[0] = W25N_PROG_EXECUTE
        cbuf[1] = (pageAdd & 0xFF0000) >> 16
        cbuf[2] = (pageAdd & 0xFF00) >> 8
        cbuf[3] = pageAdd & 0xFF
        self.sendCmd(cbuf,4)
        return 0

#  //pageIndex(add) -- get page index from address
    def pageIndex(self, pageAdd):
        return pagAdd //  W25N_PAGES_SIZE

#   //pageDataRead(add) -- Commands the flash to read from the given page address into
#   //its internal buffer, to be read using the read() function. 
#   //This command will put the flash in a busy state for a time, so busy checking is required after use.
    def pageDataRead(self, pageAdd):
        if pageAdd > self.getMaxPage():
            print(" page read add out of bounds")
            return 1
        self.dieSelectOnAdd(pageAdd)
        cbuf = bytearray(4)
        cbuf[0] = W25N_PAGE_DATA_READ
        cbuf[1] = (pageAdd & 0xFF0000) >> 16
        cbuf[2] = (pageAdd & 0x00FF00)>> 8
        cbuf[3] = pageAdd & 0x0000FF
        self.block_WIP()
        self.sendCmd(cbuf,4)
        return 0

#   //read(columnAdd, buf, dataLen) -- Reads data from the flash internal buffer
#   //columnAdd is a buffer index (0-2047) or (0 - 2111) including ECC bits
#   //datalen is the length of data that should be read from the buffer (up to 2111)
    def read(self, columnAdd, buf = None, dataLen = None):
        if columnAdd > W25N_MAX_COLUMN:
            return 1
        if dataLen:
            if dataLen > (W25N_MAX_COLUMN - columnAdd):
                return 1
        cbuf = bytearray(4)
        cbuf[0] = W25N_READ
        cbuf[1] = columnAdd >> 8
        cbuf[2] = columnAdd & 0xff
        cbuf[3] = 0x00
        self.block_WIP()
        self._cs(0)
        self._spi.write(cbuf)
        if buf is None:
            buf = self._spi.read(dataLen)
        else:
            self._spi.readinto(buf)
        self._cs(1)
        return buf

#   //check_WIP() -- checks if the flash is busy with an operation
#   //Output: true if busy, false if free
    def check_WIP(self):
        status = self.getStatusReg(W25N_STAT_REG)
        if status[2] & 0x01:
            return 1
        else:
            return 0

#   //block_WIP() -- checks if the flash is busy and only returns once free
#   //Has a 15ms timeout
    def block_WIP(self):
        #/Max WIP time is 10ms for block erase so 15 should be a max.
        count = 0
        while self.check_WIP():
            time.sleep_ms(1)
            count = count + 1
            if count > 15:
                return 1
        return 0

#   //check_Status() -- returns status register value

    def check_Status(self):
        return(self.getStatusReg(W25N_STAT_REG))
    
#   //flash_Size()  -- returns full flash size in bits

    def flash_Size(self):
        return self.size
    
#   //sector_Size() -- returns erase sector size in bits

    def sector_Size(self):
        return self.block_size
    
#   //page_Size() -- returns page size in bits

    def page_Size(self):
        return (W25N_PAGES_SIZE)
    
#   //cache_Size() return internal buffer size in bits including ECC sectors

    def cache_Size(self):
        return (W25N_CACHE_SIZE)

    

