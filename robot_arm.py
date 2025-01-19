from machine import I2C, Pin
import PCA9685
from time import sleep
from settings import (
    I2C_CONFIG, 
    SERVO_CONFIG, 
    PWM_LIMITS, 
    MOVEMENT, 
    INITIAL_POSITIONS,
    SAFETY_LIMITS,
    ERROR_MESSAGES
)

class RoboticArm:
    def __init__(self):
        # Inicializa I2C
        i2c = I2C(I2C_CONFIG['id'], sda=Pin(I2C_CONFIG['sda_pin']), scl=Pin(I2C_CONFIG['scl_pin']))
        
        # Inicializa PCA9685
        self.pca = PCA9685(i2c)
        self.pca.freq(SERVO_CONFIG['frequency'])
        
        # Pinos dos servos
        self.BASE_SERVO = SERVO_CONFIG['pins']['base']
        self.HEIGHT_SERVO = SERVO_CONFIG['pins']['height']
        self.EXTEND_SERVO = SERVO_CONFIG['pins']['extend']
        
        # Inicializa posições
        self.current_base = INITIAL_POSITIONS['base']
        self.current_height = INITIAL_POSITIONS['height']
        self.current_extend = INITIAL_POSITIONS['extend']
        
        # Controle de velocidade
        self.DEFAULT_SPEED = MOVEMENT['default_speed']
        self.current_speed = self.DEFAULT_SPEED
        
        # Limites de segurança
        self.safe_zones = SAFETY_LIMITS
        
        self.home_position()

    def angle_to_duty(self, angle: float) -> int:
        """
        Converte ângulo para ciclo de trabalho PWM.
        
        Args:
            angle: Ângulo desejado (0-180°)
            
        Returns:
            Valor do ciclo de trabalho para o servo
            
        Raises:
            ValueError: Se o ângulo estiver fora do intervalo válido
        """
        min_duty = PWM_LIMITS['min_duty']
        max_duty = PWM_LIMITS['max_duty']
        return min_duty + (angle * (max_duty - min_duty) / 180)
    
    def move_servo(self, servo_num, angle):
        """Move um servo específico para um ângulo"""
        if 0 <= angle <= 180:
            duty = self.angle_to_duty(angle)
            self.pca.set_pwm(servo_num, 0, int(duty))
        else:
            raise ValueError(ERROR_MESSAGES['angle_range'].format(min=0, max=180))
    
    # ... restante do código permanece o mesmo ...
        
    def calculate_safe_extend(self, height_angle):
        """Calcula o limite seguro de extensão baseado na altura"""
        # Relação linear simples
        # Quando a altura está no mínimo, permite extensão máxima
        # Quando a altura está no máximo, restringe a extensão
        height_factor = (height_angle - SAFETY_LIMITS['height']['min']) / (
            SAFETY_LIMITS['height']['max'] - SAFETY_LIMITS['height']['min']
        )
        max_extend = SAFETY_LIMITS['extend']['max'] - (
            height_factor * SAFETY_LIMITS['max_extension_reduction']
        )
        return max_extend
    
    def move_coordinated(self, height: float, extend: float) -> None:
        """
        Realiza movimento coordenado entre altura e extensão.
        
        Implementa verificações de segurança e sequência adequada
        para evitar colisões.
        
        Args:
            height: Ângulo desejado para altura
            extend: Ângulo desejado para extensão
            
        Raises:
            ValueError: Se o movimento for considerado inseguro
        """
        # Check height first
        self.check_safety_limits('height', height)
        
        # Calculate safe extension limit
        max_extend = self.calculate_safe_extend(height)
        if extend > max_extend:
            raise ValueError(ERROR_MESSAGES['extension_limit'].format(extend=extend, height=height, max_extend=max_extend))
        
        # Move height first if extending
        if extend > self.current_extend:
            self.move_height(height)
            self.move_extend(extend)
        # Move extend first if retracting
        else:
            self.move_extend(extend)
            self.move_height(height)
        