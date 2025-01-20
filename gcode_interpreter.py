from servo import Servos
import time
from settings import *
import math

class GCodeInterpreter:
    def __init__(self, servo):
        self.servo = servo
        self.axis_limits = AXIS_LIMITS
        self.current_position = HOME_POSITION.copy()
        self.current_speed = VELOCITY  # Usa velocidade do settings.py
        
        # Não move os servos na inicialização
        # Aguarda o setup() ser chamado explicitamente
    
    def setup(self):
        """Inicialização segura - deve ser chamada após criar a instância"""
        print("Iniciando setup do braço robótico...")
        
        # Move diretamente para home usando a velocidade configurada
        self.home()
        time.sleep(SETUP_DELAY)
        print("Setup completo!")

    def _map_axis_to_servo(self, axis):
        """Mapeia eixo para índice do servo"""
        mapping = {
            'X': 2,  # X (comprimento) agora usa servo 2
            'Y': 1,  # Y (altura) continua no servo 1
            'Z': 0   # Z (base) agora usa servo 0
        }
        return mapping.get(axis, None)

    def _validate_position(self, axis, value):
        """Valida se a posição está dentro dos limites"""
        limits = self.axis_limits[axis]
        if value < limits['min'] or value > limits['max']:
            raise ValueError(f"Posição {value} fora dos limites para eixo {axis} ({limits['min']}-{limits['max']})")
        return value

    def parse_command(self, command):
        """Interpreta e executa comandos G-code"""
        parts = command.upper().split()
        if not parts:
            return
        
        if parts[0] in ['G0', 'G1']:
            positions = {}
            for part in parts[1:]:
                if part[0] in ['X', 'Y', 'Z']:
                    axis = part[0]
                    value = float(part[1:])
                    positions[axis] = self._validate_position(axis, value)
                # Removido o processamento do F (velocidade) para manter consistência
            
            self.move_to(positions)
            
        elif parts[0] == 'G28':
            self.home()
            
        elif parts[0] == 'M114':
            return self.get_position()

    def move_to(self, positions):
        """Move todos os servos simultaneamente para as posições especificadas"""
        servo_positions = {}
        for axis, target in positions.items():
            servo_index = self._map_axis_to_servo(axis)
            if servo_index is not None:
                servo_positions[servo_index] = target
        
        # Move todos os servos de uma vez
        self.servo.position_all(servo_positions)
        
        # Atualiza as posições atuais
        self.current_position.update(positions)

    def home(self):
        """Move todos os eixos para a posição inicial com velocidade controlada"""
        self.move_to(HOME_POSITION)

    def get_position(self):
        """
        Retorna a posição atual dos servos.
        """
        # Supondo que a classe Servos tenha um método para obter a posição
        return {
            'X': self.servo.get_position(2),  # Servo 2 para X
            'Y': self.servo.get_position(1),  # Servo 1 para Y
            'Z': self.servo.get_position(0)   # Servo 0 para Z
        }