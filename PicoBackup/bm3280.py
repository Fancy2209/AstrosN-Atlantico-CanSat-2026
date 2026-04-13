from machine import I2C, Pin
import bme280_float as bme280 # Importa o ficheiro que acabou de salvar
import time

# Configuração do I2C
# GP4 (SDA) e GP5 (SCL)
i2c = I2C(0, sda=Pin(4), scl=Pin(5))

# Inicialização do sensor
# O driver do robert-hh requer o objeto i2c
bme = bme280.BME280(i2c=i2c)

print("Iniciando leitura com driver robert-hh...")

while True:
    # O método 'values' retorna uma tupla formatada: (temperatura, pressão, umidade)
    # Exemplo: ('24.50C', '1013.25hPa', '50.1%')
    t, p, h = bme.values
    
    print(f"Temperatura: {t}")
    print(f"Pressão: {p}")
    print(f"Umidade: {h}")
    print("-" * 25)
    
    time.sleep(2)