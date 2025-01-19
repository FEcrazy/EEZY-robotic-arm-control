"""
Configurações do Braço Robótico
------------------------------
Centraliza todas as configurações e parâmetros do sistema.

Autor: Felipe Delduque Guerche
"""

# Configurações do Hardware
I2C_CONFIG = {
    'id': 1,
    'sda_pin': 1,
    'scl_pin': 2
}

SERVO_CONFIG = {
    'frequency': 50,  # Frequência padrão para servos (Hz)
    'pins': {
        'base': 0,    # Pino do servo da base
        'height': 1,  # Pino do servo de altura
        'extend': 2   # Pino do servo de extensão
    }
}

# Limites de PWM
PWM_LIMITS = {
    'min_duty': 1638,  # 2% duty cycle
    'max_duty': 8192   # 10% duty cycle
}

# Configurações de Movimento
MOVEMENT = {
    'default_speed': 90,  # Velocidade padrão (graus/segundo)
    'min_speed': 1,      # Velocidade mínima
    'max_speed': 180,    # Velocidade máxima
    'controlled_speed': 45  # Velocidade para movimentos controlados (G1)
}

# Posições Iniciais (em graus)
INITIAL_POSITIONS = {
    'base': 90,
    'height': 90,
    'extend': 90
}

# Limites de Segurança (em graus)
SAFETY_LIMITS = {
    'height': {
        'min': 30,
        'max': 150
    },
    'extend': {
        'min': 30,
        'max': 150
    },
    'base': {
        'min': 0,
        'max': 180
    }
}

# Configurações de Coordenação
COORDINATION = {
    'max_extension_reduction': 30  # Redução máxima da extensão baseada na altura
}

# Configurações de Tempo
TIMING = {
    'command_delay': 0.5,  # Delay entre comandos (segundos)
}

# Comandos G-code Suportados
SUPPORTED_GCODE = {
    'G0': 'rapid_move',
    'G1': 'controlled_move',
    'G28': 'home',
    'M114': 'get_position'
}

# Mensagens de Erro
ERROR_MESSAGES = {
    'angle_range': "Ângulo deve estar entre {min} e {max}",
    'speed_range': "Velocidade deve estar entre {min} e {max} graus/segundo",
    'safety_limit': "{servo} ângulo {angle} está fora dos limites seguros ({min}-{max})",
    'extension_limit': "Extensão {extend} muito grande para altura {height}. Extensão máxima segura é {max_extend}",
    'unsupported_command': "Comando não suportado: {command}"
} 