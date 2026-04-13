from machine import I2C, Pin
import time
from bno08x import BNO08X
from bno_i2c import BNO08X_I2C

# 1. Configuração
i2c_bus = I2C(0, sda=Pin(4), scl=Pin(5), freq=400000)
pino_int = Pin(15, Pin.IN, Pin.PULL_UP)
pino_rst = Pin(14, Pin.OUT)

# 2. Inicialização com a ordem correta para o teu __init__
bno = BNO08X_I2C(i2c_bus, 0x4A, pino_rst, pino_int)

# 3. ATIVAÇÃO: Esta é a linha que faltava!
print("A ativar acelerómetro...")
bno.acceleration.enable()
print("✅ Funcionalidade ativada!")

print("A ler dados...")

while True:
    bno.update_sensors()
    accel = bno.acceleration
    
    # Como ele tem __iter__, isto funciona:
    dados = list(accel) 
    
    # Agora 'dados' é uma lista [x, y, z]
    print(f"Aceleração: X:{dados[0]:.2f} Y:{dados[1]:.2f} Z:{dados[2]:.2f}")
    
    time.sleep(0.1)
