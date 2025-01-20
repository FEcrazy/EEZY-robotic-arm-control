# Configurações do Braço Robótico

# Velocidades (0-100)
VELOCITY = 20  # Velocidade reduzida para maior precisão

# Configurações I2C
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1
I2C_ID = 0

# Delays (em segundos)
MOVEMENT_DELAY = 0.01
SETUP_DELAY = 1

# Limites dos eixos (em graus)
AXIS_LIMITS = {
    'Z': {'min': 45, 'max': 135},    # Base - centralizado em 90°
    'Y': {'min': 20, 'max': 130},     # Altura
    'X': {'min': 0, 'max': 110},     # Comprimento
}

# Posição Home
HOME_POSITION = {
    'X': 50,    # Começa esticado
    'Y': 65,                         # Altura média segura
    'Z': 90                          # Centro da rotação
}

# Configurações para linha horizontal
HORIZONTAL_LINE = {
    'Z_CENTER': 90,                  # Centro da rotação (graus)
    'Z_RANGE': 45,                   # Amplitude do movimento (± graus do centro)
    'X_COMPENSATION_GAIN': 1.2,      # Ganho da compensação de X
    'Y_COMPENSATION_GAIN': 0.3,      # Ganho da compensação de Y
    'X_EXTENDED': 80,              # Posição máxima de X
    'X_RETRACTED': 60,              # Posição mínima de X
    'Y_EXTENDED': 80,               # Posição máxima de Y
    'Y_RETRACTED': 60,              # Posição mínima de Y
    'STEP_SIZE': 1,                  # Tamanho do passo em graus
}

# Tolerâncias
POSITION_TOLERANCE = 0.5             # Tolerância para posição atingida
SERVO_TIMEOUT = 3.0                  # Timeout para movimento dos servos

# Fatores de compensação para movimento linear
# Estes valores precisarão ser ajustados com testes práticos
COMPENSATION_FACTORS = {
    'HORIZONTAL': {
        'Z_per_X': 1,  # Quanto Z muda para cada grau de X (linha horizontal)
    },
    'VERTICAL': {
        'Z_per_Y': 1.2,  # Quanto Z muda para cada grau de Y (linha vertical)
    },
    'DIAGONAL': {
        'Y_per_X': 0.3,  # Quanto Y muda para cada grau de X
        'Z_per_X': 0.8,  # Quanto Z muda para cada grau de X
    }
}

# Definições de limites para os eixos
LIMITS = {
    'X': {'min': 80, 'max': 120},  # Limites para o comprimento
    'Y': {'min': 50, 'max': 90},   # Limites para a altura
    'Z': {'min': 0, 'max': 180}    # Limites para a base
} 