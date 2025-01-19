# servo.py
# Kevin McAleer
# March 2021

from pca9685 import PCA9685
import math
import time

class Servos:
    def __init__(self, i2c, address=0x40, freq=50, min_us=600, max_us=2400,
                 degrees=180):
        self.period = 1000000 / freq
        self.min_duty = self._us2duty(min_us)
        self.max_duty = self._us2duty(max_us)
        self.degrees = degrees
        self.freq = freq
        self.pca9685 = PCA9685(i2c, address)
        self.pca9685.freq(freq)

    def _us2duty(self, value):
        return int(4095 * value / self.period)

    def position(self, index, degrees=None, radians=None, us=None, duty=None):
        span = self.max_duty - self.min_duty
        if degrees is not None:
            duty = self.min_duty + span * degrees / self.degrees
        elif radians is not None:
            duty = self.min_duty + span * radians / math.radians(self.degrees)
        elif us is not None:
            duty = self._us2duty(us)
        elif duty is not None:
            pass
        else:
            return self.pca9685.duty(index)
        duty = min(self.max_duty, max(self.min_duty, int(duty)))
        self.pca9685.duty(index, duty)

    def test_servos(self):
        """
        Move all servos from min to max position and back to test functionality.
        """
        for index in range(16):  # Assuming 16 channels on the PCA9685
            # Move to minimum position
            self.position(index, degrees=0)
            time.sleep(1)  # Wait for 1 second

            # Move to maximum position
            self.position(index, degrees=self.degrees)
            time.sleep(1)  # Wait for 1 second

            # Return to minimum position
            self.position(index, degrees=0)
            time.sleep(1)  # Wait for 1 second    

    def release(self, index):
        self.pca9685.duty(index, 0)