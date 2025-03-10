#!/usr/bin/python

import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

    # Registers/etc.
    __SUBADR1 = 0x02
    __SUBADR2 = 0x03
    __SUBADR3 = 0x04
    __MODE1 = 0x00
    __PRESCALE = 0xFE
    __LED0_ON_L = 0x06
    __LED0_ON_H = 0x07
    __LED0_OFF_L = 0x08
    __LED0_OFF_H = 0x09
    __ALLLED_ON_L = 0xFA
    __ALLLED_ON_H = 0xFB
    __ALLLED_OFF_L = 0xFC
    __ALLLED_OFF_H = 0xFD

    def __init__(self, address=0x40, debug=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.debug = debug
        if self.debug:
            print("Resetting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)
        if self.debug:
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        result = self.bus.read_byte_data(self.address, reg)
        if self.debug:
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if self.debug:
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if self.debug:
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if self.debug:
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ, period is 20000us
        self.setPWM(channel, 0, int(pulse))

# ============================================================================
# Run Count and Timestamp Tracker
# ============================================================================
  
RUN_COUNT_FILE = "/home/pi/servo_runs_open.txt"
TIMESTAMP_FILE = "/home/pi/servo_timestamps.txt"
TIME_LIMIT = 3 * 60  # 3 minutes (in seconds)
MAX_RUNS = 2
PULSE_ADJUSTMENT = 0
MIN_PULSE_LIMIT = 1500


# Function to get the run count from the file
def get_run_count():
    if os.path.exists(RUN_COUNT_FILE):
        with open(RUN_COUNT_FILE, "r") as f:
            count = f.read().strip()
            return int(count) if count else 0
    return 0


# Function to update the run count in the file
def update_run_count():
    count = get_run_count() + 1
    with open(RUN_COUNT_FILE, "w") as f:
        f.write(str(count))
    return count


# Function to get and update the timestamp list from the file
def get_timestamps():
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE, "r") as f:
            timestamps = f.read().strip().splitlines()
            return [float(timestamp) for timestamp in timestamps] if timestamps>
    return []


# Function to update the timestamp list and manage cleanup
def update_timestamps(current_time):
    # Get existing timestamps
    timestamps = get_timestamps()

    # Add the current timestamp
    timestamps.append(current_time)

    # Remove any timestamps older than TIME_LIMIT (3 minutes)
    timestamps = [timestamp for timestamp in timestamps if current_time - times>

    # Write the updated timestamps to the file
    with open(TIMESTAMP_FILE, "w") as f:
        for timestamp in timestamps:
            f.write(f"{timestamp}\n")

    return timestamps


# Function to adjust pulse values based on script usage
def adjust_pulse_values():
    current_time = time.time()

    # Get updated timestamps (which also handles cleaning up old ones)
    timestamps = update_timestamps(current_time)

    # Check how many times the script has been run in the last 3 minutes
    if len(timestamps) > MAX_RUNS:
        print(f"Run limit exceeded. Adjusting pulse values.")
        return PULSE_ADJUSTMENT  # Adjust pulse values as needed
    return 0  # No adjustment if the limit is not exceeded


def stop_servos(pwm, channel=15):
    pwm.setServoPulse(channel, 0) # Stop only the channel used
    print(f"Servo on channel {channel} stopped.")


def main():
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)  # Set frequency to 50Hz

    try:
        min_pulse = 1653
        mid_pulse = 1766
        max_pulse = 1800

        # Perform the adjustment check
        pulse_adjustment = adjust_pulse_values()

        # If pulse adjustment is needed, adjust the pulse range
        if pulse_adjustment > 0:
            min_pulse += pulse_adjustment
            mid_pulse += pulse_adjustment
            max_pulse += pulse_adjustment
            print(f"Adjusted pulse range by {pulse_adjustment} due to over usag>

        # Move the servo
        for i in range(mid_pulse, min_pulse, -7):
            pwm.setServoPulse(15, i)  # Operate on channel 15
            time.sleep(0.1)
        pwm.setServoPulse(15, 0) #Stop channel 15

        stop_servos(pwm)

        time.sleep(2)

        for i in range(max_pulse, mid_pulse, -7):
            pwm.setServoPulse(15, i)  # Operate on channel 15
            time.sleep(0.1)
        pwm.setServoPulse(0, 0)

        stop_servos(pwm)  # Stop servos after completion

    except KeyboardInterrupt:
        print("Exiting program")
        stop_servos(pwm)
    except Exception as e:
        print(f"Error: {e}")
        stop_servos(pwm)


if __name__ == '__main__':
    main()
