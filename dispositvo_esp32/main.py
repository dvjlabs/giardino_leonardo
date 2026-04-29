import dht
import ds18x20
import network
import time
import onewire
import requests
from machine import Pin, I2C, ADC
from I2C_LCD import I2cLcd

# --- CONFIGURAZIONE ---
MIN_VALUE = 0
MAX_VALUE = 1700
MOISTURE_PIN = 34
DS_PIN_NUM = 32
tempo = 60

# Connessione WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('WifiDaVinci', 'LeonardoDaVinci!')
while not wlan.isconnected():
    print("Connecting...")
    time.sleep(0.5)
print("CONNECTED:", wlan.ifconfig())

# Setup Sensori
led = Pin(5, Pin.OUT)
ds_pin = Pin(DS_PIN_NUM)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
adc = ADC(Pin(MOISTURE_PIN))
adc.atten(ADC.ATTN_11DB)
adc.width(ADC.WIDTH_12BIT)

# Inizializzazione LCD (Spostata fuori dal loop)
i2c = I2C(scl=Pin(21), sda=Pin(22), freq=400000)
devices = i2c.scan()
lcd = None
if devices:
    lcd = I2cLcd(i2c, devices[0], 2, 16)
    lcd.putstr("Sistema Avviato")
else:
    print("Nessun LCD trovato!")

#Setup DS18B20
roms = ds_sensor.scan()
if not roms:
    raise Exception("Sensore DS18B20 non trovato")
rom = roms[0]

def converti_in_perc(value):
    perc = (value - MIN_VALUE) * 100 / (MAX_VALUE - MIN_VALUE)
    return max(0, min(100, perc)) # Limita tra 0 e 100

dht_sensor = dht.DHT11(Pin(18))
dht_sensor.measure()
aria_temp = dht_sensor.temperature()
aria_hum = dht_sensor.humidity()


while True:
    led.value(0) # Accendo led per segnalare attività
   
    #Lettura Temperatura (richiede tempo)
    ds_sensor.convert_temp()
    time.sleep(1) # Tempo necessario per la conversione
    temp = ds_sensor.read_temp(rom)
   
    # Lettura Umidità
    moisture_value = adc.read()
    moisture_percentage = converti_in_perc(moisture_value)
   
    # Stampa Console
    print(f"Umidità: {moisture_percentage:.1f}% | Temp: {temp}°C")
   
    # 1. Ottieni la tupla con i dati correnti
    # Formato: (anno, mese, giorno, ora, minuto, secondo, giorno_settimana, giorno_anno)
    t = time.localtime()

    # 2. Formatta la stringa in formato ISO (AAAA-MM-GG HH:MM)
    data_ora_iso = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4])

    # Invio Dati
    data = {
        "soilHum": moisture_percentage,
        "sensore": "Paperella",
        "soilTemp": temp,
        "airTemp": aria_temp,
        "airHum": aria_hum,
        "dataOra": data_ora_iso
    }
   
    try:
        response = requests.post("http://192.168.30.243:8000/data", json=data, timeout=5)
        print('Inviato con successo')
        response.close() # Chiudi sempre la connessione per liberare RAM
    except Exception as e:
        print('Errore invio:', e)
       
    # Aggiornamento LCD
    if lcd:
        try:
            lcd.clear()
            lcd.move_to(0, 0)
            lcd.putstr(f"Umid: {moisture_percentage:.1f}%")
            lcd.move_to(0, 1)
            lcd.putstr(f"Temp: {temp:.1f}C")
        except:
            print("Errore LCD")

    led.value(1) # Spengo led
    time.sleep(tempo) # Attesa tra le letture

