#!/usr/bin/python

import time
import math
import smbus
import signal
import os
import subprocess

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:
    # Registers/etc.
    __SUBADR1            = 0x02
    __SUBADR2            = 0x03
    __SUBADR3            = 0x04
    __MODE1              = 0x00
    __PRESCALE           = 0xFE
    __LED0_ON_L          = 0x06
    __LED0_ON_H          = 0x07
    __LED0_OFF_L         = 0x08
    __LED0_OFF_H         = 0x09
    __ALLLED_ON_L        = 0xFA
    __ALLLED_ON_H        = 0xFB
    __ALLLED_OFF_L       = 0xFC
    __ALLLED_OFF_H       = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def read(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def setPWMFreq(self, freq):
        prescaleval = 25000000.0 / 4096.0 / float(freq) - 1.0
        prescale = math.floor(prescaleval + 0.5)
        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10
        self.write(self.__MODE1, newmode)
        self.write(self.__PRESCALE, int(prescale))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)

    def setServoPulse(self, channel, pulse):
        pulse = pulse * 4096 / 20000
        self.setPWM(channel, 0, int(pulse))

# Function to stop the script gracefully
def signal_handler(sig, frame):
    print("Gracefully exiting...")
    exit(0)

# Register signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Function to check if 'open_small.py' is running
def is_open_small_running():
    try:
        # Check if 'open_small.py' is running
        result = subprocess.run(['pgrep', '-f', 'open_small.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:  # If the process is found, returncode will be 0
            return True
    except Exception as e:
        print(f"Error checking process: {e}")
    return False

if __name__ == '__main__':
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)

    # Infinite loop to keep the script running
    while True:
        try:
            # Check if open_small.py is running
            if is_open_small_running():
                print("open_small.py is running. Stopping servo control.")
                break  # Exit the loop and stop the script
            
            # Move servo to 1883-1890 range repeatedly
            min_pulse = 1883
            max_pulse = 1890
            for i in range(max_pulse, min_pulse, -7):
                pwm.setServoPulse(0, i)
                time.sleep(0.1)  

            # Set to 1675
            pwm.setServoPulse(0, 1675)
            time.sleep(0.1)

        except KeyboardInterrupt:
            print("Interrupt received, stopping...")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(1)
