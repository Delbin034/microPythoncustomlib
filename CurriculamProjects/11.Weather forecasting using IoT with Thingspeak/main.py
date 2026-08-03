# ============================================================
#  DHT11 Temperature & Humidity → ThingSpeak
#  Pins: DHT11 DATA → GPIO 4
#        LED       → GPIO 2
# ============================================================

from thingspeak import ThingSpeak
from systemio   import run
from machine    import Pin
import dht
import time

WIFI_SSID     = "YourWiFi"
WIFI_PASSWORD = "YourPassword"
TS_WRITE_KEY  = "YOUR_WRITE_API_KEY"

DHT_PIN = 4
LED_PIN = 2

ts     = ThingSpeak(TS_WRITE_KEY, WIFI_SSID, WIFI_PASSWORD)
sensor = dht.DHT11(Pin(DHT_PIN))

def setup():
    ts.digital_out(LED_PIN)

def main():
    setup()
    while True:
        ts.keep_alive()

        try:
            sensor.measure()
            temp = sensor.temperature()
            humi = sensor.humidity()
            print(f"Temp: {temp}C  Humidity: {humi}%")
            ts.digital_write(LED_PIN, 1)
            ts.send(field1=temp, field2=humi)
            ts.digital_write(LED_PIN, 0)

        except Exception as e:
            print("DHT11 Error:", e)

        time.sleep(15)

def cleanup():
    ts.all_off()

run(main, cleanup)
