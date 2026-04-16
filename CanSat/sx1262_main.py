from machine import Pin, SPI, I2C, UART, PWM, ADC
import time
import os

# Importação das bibliotecas conforme as tuas fontes
from sx1262 import SX1262

# --- CONFIGURAÇÃO DE PINOS (GP / FÍSICO) ---
# GPS: GP0/GP1 (Físico 1/2) [1]
# LoRa: SPI1 (10,11,12), CS:3, RST:15, BUSY:2, IRQ:20 [2]
# ANT_SW: GP22 (Físico 29) - Configurado como saída para o rádio
# Buzzer: GP21 (Físico 27)
# I2C: GP4/GP5 (Físico 6/7) [3]
# BNO085 Extra: RST:14, INT:6
# SD: SPI0 (16,17,18,19) [4]

# 5. LORA SX1262 (SPI1)
try:
    sx = SX1262(spi_bus=1, clk=10, mosi=11, miso=12, cs=3, irq=20, rst=15, gpio=2)

# LoRa
    sx.begin(freq=433.450, bw=500.0, sf=12, cr=8, syncWord=0x12,
         power=-5, currentLimit=60.0, preambleLength=8,
         implicit=False, implicitLen=0xFF,
         crcOn=True, txIq=False, rxIq=False,
         tcxoVoltage=1.7, useRegulatorLDO=False, blocking=True)
    print("✅ LoRa: 433MHz Pronto.")
except Exception as e:
    print("❌ LoRa: Erro de hardware (Verifica o GP2/Pino 4!).", e)
    raise SystemExit

# 6. MONITOR DE BATERIA (ADC Interno)
vsys_adc = ADC(29)

def ler_bateria():
    return vsys_adc.read_u16() * (3 * 3.3 / 65535)

# --- LOOP DE TESTE PRINCIPAL ---
print("\n--- INICIANDO TESTE DE SISTEMA ---")

while True:
    print("\n" + "="*30)
    
    # Teste LoRa (Envio de sinal)
    #try:
    msg = str(ler_bateria())
    sx.send(msg.encode())
    print(f"LoRa: Enviado -> {msg}")
    #except: print("LoRa: Falha no envio")

    time.sleep(5)