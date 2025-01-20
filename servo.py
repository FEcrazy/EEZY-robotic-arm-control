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
        
        # Armazena a última posição conhecida de cada servo
        self.last_position = {}

    def _us2duty(self, value):
        return int(4095 * value / self.period)

    def _angle_to_duty(self, angle):
        """Converte ângulo em graus para valor de duty cycle"""
        duty_range = self.max_duty - self.min_duty
        return self.min_duty + (duty_range * angle / self.degrees)

    def position(self, index, degrees=None, velocity=None):
        """
        Move o servo para a posição especificada
        
        :param index: índice do servo
        :param degrees: posição em graus (0-180)
        :param velocity: velocidade (0.0-1.0, onde 1.0 é mais rápido)
        """
        if degrees is None:
            return self.last_position.get(index, 0)

        # Limita os graus ao intervalo válido
        degrees = min(max(0, degrees), self.degrees)
        
        # Converte graus para duty cycle
        target_duty = self._angle_to_duty(degrees)
        
        # Usa velocidade constante
        if velocity is None:
            velocity = 1.0
        
        # Calcula o delay fixo baseado na velocidade
        # velocity 1.0 = 0.001s delay, velocity 0.0 = 0.02s delay
        step_delay = 0.001 + (1.0 - velocity) * 0.019
        
        # Move o servo em incrementos fixos
        if index in self.last_position:
            current_pos = self.last_position[index]
            step = 1 if degrees > current_pos else -1
            
            for pos in range(int(current_pos), int(degrees), step):
                duty = self._angle_to_duty(pos)
                self.pca9685.duty(index, int(duty))
                time.sleep(step_delay)  # Delay constante baseado na velocidade
        
        # Define a posição final
        self.pca9685.duty(index, int(target_duty))
        self.last_position[index] = degrees

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
        """Desliga o servo"""
        self.pca9685.duty(index, 0)
        if index in self.last_position:
            del self.last_position[index]

    def position_all(self, positions):
        """
        Move múltiplos servos simultaneamente
        
        :param positions: dicionário com {index: degrees}
        """
        # Primeiro calcula todos os duty cycles
        duties = {}
        for index, degrees in positions.items():
            degrees = min(max(0, degrees), self.degrees)
            span = self.max_duty - self.min_duty
            duty = self.min_duty + span * degrees / self.degrees
            duties[index] = int(duty)
        
        # Depois move todos os servos de uma vez
        for index, duty in duties.items():
            self.pca9685.duty(index, duty)
            self.last_position[index] = degrees

    def get_position(self, index):
        """
        Retorna a posição atual do servo no índice especificado.
        """
        # Este método precisa ser implementado de acordo com o hardware
        # Exemplo fictício:
        return self.last_position.get(index, 0)