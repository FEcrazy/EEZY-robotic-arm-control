"""
Interpretador de Comandos G-code
-------------------------------
Implementa um interpretador básico de G-code para controle do braço robótico.

Comandos Suportados:
    G0: Movimento rápido
    G1: Movimento controlado
    G28: Retorno à posição inicial
    M114: Consulta de posição

Autor: [Felipe Delduque Guerche]
"""

class GCodeInterpreter:
    """
    Interpretador de comandos G-code para braço robótico.
    
    Responsável por:
        - Parsing de comandos G-code
        - Execução de movimentos
        - Controle de velocidade
        - Relatório de posição
    """

    def __init__(self, robot_arm):
        """
        Inicializa o interpretador.
        
        Args:
            robot_arm: Instância de RoboticArm para controle
        """
        self.arm = robot_arm
        self.supported_commands = {
            'G0': self.rapid_move,
            'G1': self.controlled_move,
            'G28': self.home,
            'M114': self.get_position
        }
    
    def parse_coordinate(self, coord_str):
        """Converte string de coordenada para valor numérico"""
        return float(coord_str[1:])
    
    def rapid_move(self, params):
        """G0: Movimento rápido"""
        try:
            if 'B' in params:  # Base
                self.arm.move_base(self.parse_coordinate(params['B']))
            if 'H' in params and 'E' in params:  # Altura e Extensão
                self.arm.move_coordinated(
                    self.parse_coordinate(params['H']),
                    self.parse_coordinate(params['E'])
                )
            elif 'H' in params:  # Apenas altura
                self.arm.move_height(self.parse_coordinate(params['H']))
            elif 'E' in params:  # Apenas extensão
                self.arm.move_extend(self.parse_coordinate(params['E']))
        except ValueError as e:
            print(f"Erro de movimento: {e}")
    
    def controlled_move(self, params):
        """G1: Movimento controlado"""
        # Define velocidade reduzida para movimento controlado
        velocidade_original = self.arm.current_speed
        self.arm.set_speed(45)  # Metade da velocidade
        self.rapid_move(params)
        self.arm.set_speed(velocidade_original)
    
    def home(self, params):
        """G28: Home position"""
        self.arm.home_position()
    
    def get_position(self, params):
        """M114: Get current position"""
        return {
            'B': self.arm.current_base,
            'H': self.arm.current_height,
            'E': self.arm.current_extend
        }
    
    def execute(self, command: str) -> dict:
        """
        Executa um comando G-code.
        
        Args:
            command: String contendo o comando G-code
            
        Returns:
            Dicionário com resultado da operação (para M114)
            
        Raises:
            ValueError: Se o comando for inválido
        """
        # Parse command
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0]
        params = {}
        
        # Parse parameters
        for part in parts[1:]:
            if part[0] in ['B', 'H', 'E']:
                params[part[0]] = part
        
        # Execute command
        if cmd in self.supported_commands:
            return self.supported_commands[cmd](params)
        else:
            print(f"Unsupported command: {cmd}") 