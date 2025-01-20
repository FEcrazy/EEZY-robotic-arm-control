from pca9685 import PCA9685
from machine import I2C, Pin
from servo import Servos
from gcode_interpreter import GCodeInterpreter
from settings import (
    AXIS_LIMITS, 
    I2C_SDA_PIN, 
    I2C_SCL_PIN, 
    I2C_ID, 
    HOME_POSITION, 
    SETUP_DELAY, 
    MOVEMENT_DELAY, 
    HORIZONTAL_LINE,
    DIAGONAL_LINE
)
import time
import math

def calculate_compensation(z_angle, z_start, z_end):
    """
    Calcula a compensação dos eixos X e Y baseado no ângulo de Z.
    
    Args:
        z_angle: ângulo atual de Z
        z_start: ângulo inicial de Z
        z_end: ângulo final de Z
    
    Returns:
        tuple (x_pos, y_pos): Posições calculadas para X e Y
    """
    # Calcula o ponto médio do movimento de Z
    z_middle = (z_start + z_end) / 2
    
    # Calcula a distância do ponto atual até o ponto médio
    distance_to_middle = abs(z_angle - z_middle)
    
    # Calcula a amplitude total do movimento de Z
    total_amplitude = abs(z_end - z_start)
    
    # Normaliza a distância (0 = meio do movimento, 1 = extremidades)
    normalized_distance = (distance_to_middle / (total_amplitude / 2))
    
    # Aplica o ganho de compensação de X
    x_factor = normalized_distance * HORIZONTAL_LINE['X_COMPENSATION_GAIN']
    
    # Calcula posição de X
    x_range = HORIZONTAL_LINE['X_EXTENDED'] - HORIZONTAL_LINE['X_RETRACTED']
    x_pos = HORIZONTAL_LINE['X_RETRACTED'] + (x_range * x_factor)
    
    # Aplica o ganho de compensação de Y (similar ao X)
    y_factor = normalized_distance * HORIZONTAL_LINE['Y_COMPENSATION_GAIN']
    
    # Calcula posição de Y
    y_range = HORIZONTAL_LINE['Y_EXTENDED'] - HORIZONTAL_LINE['Y_RETRACTED']
    y_pos = HORIZONTAL_LINE['Y_RETRACTED'] + (y_range * y_factor)
    
    return x_pos, y_pos

def wait_for_servos(gcode, target_positions, tolerance=0.5, timeout=5.0):
    """
    Aguarda ate que todos os servos atinjam suas posicoes alvo
    """
    start_time = time.time()
    while True:
        current_pos = gcode.get_position()
        all_reached = True
        
        for axis, target in target_positions.items():
            if abs(current_pos[axis] - target) > tolerance:
                all_reached = False
                print(f"Aguardando eixo {axis}: atual={current_pos[axis]:.1f}, alvo={target:.1f}")
                break
        
        if all_reached:
            print(f"Posicao atingida: {current_pos}")
            return True
            
        if time.time() - start_time > timeout:
            print(f"Timeout! Posicao atual: {current_pos}")
            print(f"Posicao alvo: {target_positions}")
            return False
            
        time.sleep(0.1)

def execute_horizontal_line():
    """
    Executa o movimento de linha horizontal
    """
    # Define os ângulos de início e fim para Z
    z_start = 35    
    z_end = 155     
    step = HORIZONTAL_LINE['STEP_SIZE']
    
    print(f"\nIniciando movimento de Z={z_start}° ate Z={z_end}°")
    print(f"X vai variar entre {HORIZONTAL_LINE['X_RETRACTED']}° e {HORIZONTAL_LINE['X_EXTENDED']}°")
    print(f"Y vai variar entre {HORIZONTAL_LINE['Y_RETRACTED']}° e {HORIZONTAL_LINE['Y_EXTENDED']}°")
    
    # Move para posição inicial em sequência
    print("\nIndo para posicao inicial...")
    
    # 1. Primeiro move Y para posição segura
    safe_y = HORIZONTAL_LINE['Y_RETRACTED']
    print(f"1. Ajustando Y para altura segura: {safe_y}°")
    gcode.move_to({'Y': safe_y})
    if not wait_for_servos(gcode, {'Y': safe_y}, timeout=10.0):
        print("Erro ao ajustar Y!")
        return False
    
    # 2. Depois ajusta X
    initial_x = calculate_compensation(z_start, z_start, z_end)[0]  # Pega só X
    print(f"2. Ajustando X para: {initial_x}°")
    gcode.move_to({'X': initial_x})
    if not wait_for_servos(gcode, {'X': initial_x}, timeout=10.0):
        print("Erro ao ajustar X!")
        return False
    
    # 3. Por último move Z
    print(f"3. Ajustando Z para: {z_start}°")
    gcode.move_to({'Z': z_start})
    if not wait_for_servos(gcode, {'Z': z_start}, timeout=10.0):
        print("Erro ao ajustar Z!")
        return False
    
    # Verifica posição inicial
    current_pos = gcode.get_position()
    print("\nPosicao inicial atingida:")
    print(f"Y={current_pos['Y']}° X={current_pos['X']}° Z={current_pos['Z']}°")
    
    # Executa o movimento
    print("\nExecutando movimento...")
    for z in range(z_start, z_end + step, step):
        x, y = calculate_compensation(z, z_start, z_end)
        
        print(f"\nPasso atual: Z={z}°")
        print(f"Calculado X={x:.1f}°, Y={y:.1f}°")
        
        # Move um eixo por vez para melhor controle
        print("Movendo X...")
        gcode.move_to({'X': x})
        if not wait_for_servos(gcode, {'X': x}, timeout=5.0):
            print("Erro ao mover X!")
            return False
            
        print("Movendo Y...")
        gcode.move_to({'Y': y})
        if not wait_for_servos(gcode, {'Y': y}, timeout=5.0):
            print("Erro ao mover Y!")
            return False
            
        print("Movendo Z...")
        gcode.move_to({'Z': z})
        if not wait_for_servos(gcode, {'Z': z}, timeout=5.0):
            print("Erro ao mover Z!")
            return False
        
        # Verifica posição atual
        current_pos = gcode.get_position()
        print(f"Posicao atual: Y={current_pos['Y']}° X={current_pos['X']}° Z={current_pos['Z']}°")
        
        time.sleep(MOVEMENT_DELAY)
    
    return True

def execute_diagonal_line(z_start, z_end):
    """
    Executa movimento diagonal:
    - Y sobe linearmente do ponto mais baixo ao mais alto
    - X mantem compensacao similar a linha horizontal
    - Z move linearmente do fim ao inicio
    """
    step = DIAGONAL_LINE['STEP_SIZE']
    
    # Define pontos inicial e final de Y
    y_start = DIAGONAL_LINE['Y_START']
    y_end = DIAGONAL_LINE['Y_END']
    
    print(f"\nIniciando movimento diagonal:")
    print(f"Z: {z_start} -> {z_end}")
    print(f"Y: {y_start} -> {y_end}")
    
    # Calcula quantos passos teremos no total
    total_steps = abs(z_end - z_start) // step
    y_step = (y_end - y_start) / total_steps
    
    # Executa o movimento
    print("\nExecutando movimento diagonal...")
    current_y = y_start
    
    for z in range(z_start, z_end - step, -step):
        # Calcula X usando a mesma logica da linha horizontal
        x_pos = calculate_compensation(z, z_start, z_end)[0]  # Pega so X
        
        print(f"\nPasso atual: Z={z}")
        print(f"X={x_pos:.1f}, Y={current_y:.1f}")
        
        # Move um eixo por vez para melhor controle
        print("Movendo X...")
        gcode.move_to({'X': x_pos})
        if not wait_for_servos(gcode, {'X': x_pos}, timeout=5.0):
            print("Erro ao mover X!")
            return False
            
        print("Movendo Y...")
        gcode.move_to({'Y': current_y})
        if not wait_for_servos(gcode, {'Y': current_y}, timeout=5.0):
            print("Erro ao mover Y!")
            return False
            
        print("Movendo Z...")
        gcode.move_to({'Z': z})
        if not wait_for_servos(gcode, {'Z': z}, timeout=5.0):
            print("Erro ao mover Z!")
            return False
        
        # Verifica posicao atual
        current_pos = gcode.get_position()
        print(f"Posicao atual: Y={current_pos['Y']:.1f} X={current_pos['X']:.1f} Z={current_pos['Z']:.1f}")
        
        # Incrementa Y linearmente
        current_y += y_step
        time.sleep(MOVEMENT_DELAY)
    
    return True

# No programa principal:
if __name__ == "__main__":
    # Configuração do I2C
    sda = Pin(I2C_SDA_PIN)
    scl = Pin(I2C_SCL_PIN)
    i2c = I2C(id=I2C_ID, sda=sda, scl=scl)

    # Inicialização dos objetos
    pca = PCA9685(i2c=i2c)
    servo = Servos(i2c=i2c)
    gcode = GCodeInterpreter(servo)

    print("Iniciando sequência de movimentos...")

    # 1. Primeiro vai para home
    print("\n1. Indo para posição home...")
    gcode.parse_command("G28")
    time.sleep(SETUP_DELAY)
    
    # Verifica se chegou em home
    home_pos = gcode.get_position()
    print(f"Posição home: X={home_pos['X']}° Y={home_pos['Y']}° Z={home_pos['Z']}°")

    # 2. Define posição inicial do movimento
    z_start = 45  # Posição inicial de Z
    x_start = 90  # Posição inicial de X
    y_safe = 65   # Altura segura de Y
    
    # 3. Move para posição inicial
    print("\n2. Indo para posição inicial do movimento...")
    
    # Primeiro ajusta Y para altura segura
    print("Ajustando altura...")
    gcode.move_to({'Y': y_safe})
    if not wait_for_servos(gcode, {'Y': y_safe}, timeout=10.0):
        print("Erro ao ajustar altura!")
        exit()
    
    # Depois ajusta X
    print("Ajustando comprimento...")
    gcode.move_to({'X': x_start})
    if not wait_for_servos(gcode, {'X': x_start}, timeout=10.0):
        print("Erro ao ajustar comprimento!")
        exit()
    
    # Por último ajusta Z
    print("Ajustando base...")
    gcode.move_to({'Z': z_start})
    if not wait_for_servos(gcode, {'Z': z_start}, timeout=10.0):
        print("Erro ao ajustar base!")
        exit()
    
    # 4. Verifica posição inicial
    current_pos = gcode.get_position()
    print("\nVerificando posição inicial:")
    print(f"Alvo    : X={x_start}° Y={y_safe}° Z={z_start}°")
    print(f"Atual   : X={current_pos['X']}° Y={current_pos['Y']}° Z={current_pos['Z']}°")
    
    # Verifica se está na posição correta
    if (abs(current_pos['X'] - x_start) > 1 or 
        abs(current_pos['Y'] - y_safe) > 1 or 
        abs(current_pos['Z'] - z_start) > 1):
        print("ERRO: Posição inicial não atingida corretamente!")
        exit()
    
    print("\nPosição inicial OK! Aguardando início do movimento...")
    time.sleep(SETUP_DELAY)

    # Executa movimento horizontal
    if execute_horizontal_line():
        print("\nLinha horizontal concluida com sucesso!")
        
        # Pega posição atual de Z para iniciar movimento diagonal
        current_pos = gcode.get_position()
        z_atual = current_pos['Z']
        
        # Executa movimento diagonal
        print("\nIniciando movimento diagonal...")
        if execute_diagonal_line(z_atual, 35):  # 35 é o z_start original do movimento horizontal
            print("\nLinha diagonal concluida com sucesso!")
        else:
            print("\nErro ao executar linha diagonal!")
    else:
        print("\nErro ao executar linha horizontal!")

    print("\nRetornando ao home...")
    gcode.parse_command("G28")
    time.sleep(MOVEMENT_DELAY)

    print("\nDesligando servos...")
    servo.release(2)  # X
    servo.release(1)  # Y
    servo.release(0)  # Z

    print("\nSequencia completa! Servos desligados.")