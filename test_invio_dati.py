import requests
import datetime
import random
import time

IP_INVIO_DATI = "127.0.0.1" # "192.168.30.243"
PORTA_INVIO_DATI = 5000     # 8000

def send_data(payload):
    try:
        response = requests.post(f"http://{IP_INVIO_DATI}:{PORTA_INVIO_DATI}/data", json=payload)
        print('Response content:', response.text)
    except Exception as e:
        print('An error occurred during the request:', str(e))
    return

data = {}

for n in range(15):
    data["sensore"] = "sensor" + str(n % 4)
    mezzanotte = datetime.datetime(2026,4,4,0,0,0)
    tempo = datetime.timedelta(minutes=n*60)
    dataOra = mezzanotte + tempo
    data["dataOra"] = dataOra.isoformat()
    data["airTemp"] = random.randint(1,100)
    data["airHum"] = random.randint(1,100)
    data["soilTemp"] = random.randint(1,100)
    data["soilHum"] = random.randint(1,100)
    send_data(data)
    time.sleep(0.1)
