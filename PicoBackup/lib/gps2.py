from machine import UART, Pin
import time

# Configura a UART1 (GP4=TX, GP5=RX)
# O baudrate padrão do Adafruit GPS é 9600
uart1 = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

print("Lendo dados do GPS na UART1... (Ctrl+C para parar)")

while True:
    if uart1.any():
        try:
            # Lê a linha e remove espaços extras
            print("uart")
            linha = uart1.readline()
            if linha:
                print(linha.decode('utf-8').strip())
        except UnicodeError:
            # Caso receba um caractere estranho no início
            pass
    time.sleep(0.1)