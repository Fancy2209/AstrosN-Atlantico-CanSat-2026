import machine
import sdcard
import os
import time

# 1. Configuração do Hardware (SPI0 nos teus pinos)
spi = machine.SPI(0, baudrate=1000000, polarity=0, phase=0, 
                  sck=machine.Pin(18), mosi=machine.Pin(19), miso=machine.Pin(16))
cs = machine.Pin(17, machine.Pin.OUT)

# 2. Inicialização do Cartão SD
try:
    sd = sdcard.SDCard(spi, cs)
    vfs = os.VfsFat(sd)
    os.mount(vfs, "/sd")
    print("Cartão SD montado com sucesso!")
except Exception as e:
    print("Erro ao montar cartão: ", e)
    # Para o programa se o cartão não estiver presente
    raise SystemExit 

# 3. Configuração do Sensor de Temperatura Interno do Pico
sensor_temp = machine.ADC(4)
fator_conversao = 3.3 / 65535

# 4. Criar o cabeçalho do ficheiro CSV (se o ficheiro não existir)
filename = "/sd/log_temperatura.csv"
if not filename in os.listdir("/sd"):
    with open(filename, "w") as f:
        f.write("Segundos_desde_inicio,Temperatura_C\n")

print("A iniciar gravação... Prime Ctrl+C para parar.")

# 5. Loop de Leitura e Gravação
segundos = 0
try:
    while True:
        # Leitura analógica e conversão para Celsius
        leitura = sensor_temp.read_u16() * fator_conversao
        # Fórmula oficial da Raspberry Pi para o sensor interno
        temperatura = 27 - (leitura - 0.706) / 0.001721
        
        # Guardar no cartão SD
        with open(filename, "a") as f:
            f.write(f"{segundos},{temperatura:.2f}\n")
        
        print(f"Log: {segundos}s -> {temperatura:.2f}°C gravado.")
        
        # Espera 5 segundos
        time.sleep(5)
        segundos += 5
        
except KeyboardInterrupt:
    print("\nGravação interrompida pelo utilizador.")
    os.umount("/sd")
    print("Cartão desmontado com segurança.")