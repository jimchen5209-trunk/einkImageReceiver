# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.2
# * | Date        :   2022-10-29
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import sys


class MicroPython:

    def __init__(self):
        from machine import Pin  # pylint: disable=C0415
        self.CS_PIN = self.cs = Pin(15)
        self.DC_PIN = self.dc = Pin(27)
        self.RST_PIN = self.rst = Pin(26)
        self.BUSY_PIN = self.busy = Pin(25)

    def digital_write(self, pin, value):
        pin(value)

    def digital_read(self, pin):
        return pin.value()

    def spi_writebyte(self, data):
        self.spi.write(bytes(c & 0xff for c in data))

    def spi_writebyte2(self, data):
        self.spi_writebyte(data)

    def delay_ms(self, delaytime):
        import utime  # pylint: disable=C0415
        utime.sleep_ms(delaytime)

    def module_init(self):
        from machine import Pin, SPI  # pylint: disable=C0415
        clk = Pin(13)
        mosi = Pin(14)
        miso = Pin(26)
        self.spi = SPI(2, baudrate=20000000, polarity=0, phase=0, sck=clk, miso=miso, mosi=mosi)
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        print('init')
        return 0

    def module_exit(self):
        self.spi.deinit()


implementation = MicroPython()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))

### END OF FILE ###
