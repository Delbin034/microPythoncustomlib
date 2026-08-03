from thingspeak import ThingSpeak
from systemio   import run
import time

WIFI_SSID     = "XXXX"
WIFI_PASSWORD = "XXXX@321#"
TS_WRITE_KEY  = "KLYLQJAZKWWLCPELXK"

MQ3_PIN = 34
LED_PIN  = 4

ts = ThingSpeak(TS_WRITE_KEY, WIFI_SSID, WIFI_PASSWORD)

def setup():
    ts.analog_pin(MQ3_PIN)
    ts.digital_out(LED_PIN)

def main():
    setup()
    while True:
        ts.keep_alive()
        air_quality = 100 - ts.analog_average_percent(MQ3_PIN, 10)
        status = "High" if air_quality > 60 else ("Ok" if air_quality > 30 else "Low!")
        print(f"AirQuality: {air_quality}%  Status: {status}")
        ts.digital_write(LED_PIN, 1 if air_quality < 30 else 0)
        ts.send(field1=air_quality)
        time.sleep(2)

def cleanup():
    ts.all_off()

run(main, cleanup)