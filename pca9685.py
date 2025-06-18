# MicroPython-compatible PCA9685 Driver (Adafruit-style)
from machine import I2C
import time
import math

# Registers
PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE
LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09
ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# Bits
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01
INVRT              = 0x10
OUTDRV             = 0x04

class PCA9685:
    def __init__(self, i2c: I2C, address=PCA9685_ADDRESS):
        self.i2c = i2c
        self.address = address
        self.set_all_pwm(0, 0)
        self._write8(MODE2, OUTDRV)
        self._write8(MODE1, ALLCALL)
        time.sleep_ms(5)
        mode1 = self._read8(MODE1)
        mode1 = mode1 & ~SLEEP
        self._write8(MODE1, mode1)
        time.sleep_ms(5)

    def _write8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def _read8(self, reg):
        return int.from_bytes(self.i2c.readfrom_mem(self.address, reg, 1), 'little')

    def set_pwm_freq(self, freq_hz):
        prescaleval = 25000000.0
        prescaleval /= 4096.0
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        prescale = int(math.floor(prescaleval + 0.5))

        oldmode = self._read8(MODE1)
        newmode = (oldmode & 0x7F) | 0x10
        self._write8(MODE1, newmode)
        self._write8(PRESCALE, prescale)
        self._write8(MODE1, oldmode)
        time.sleep_ms(5)
        self._write8(MODE1, oldmode | RESTART)

    def set_pwm(self, channel, on, off):
        self._write8(LED0_ON_L + 4 * channel, on & 0xFF)
        self._write8(LED0_ON_H + 4 * channel, on >> 8)
        self._write8(LED0_OFF_L + 4 * channel, off & 0xFF)
        self._write8(LED0_OFF_H + 4 * channel, off >> 8)

    def set_all_pwm(self, on, off):
        self._write8(ALL_LED_ON_L, on & 0xFF)
        self._write8(ALL_LED_ON_H, on >> 8)
        self._write8(ALL_LED_OFF_L, off & 0xFF)
        self._write8(ALL_LED_OFF_H, off >> 8)
