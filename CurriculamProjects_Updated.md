# 🤖 ESP32 MicroPython Projects — Student Curriculum

A hands-on project collection for learning **ESP32 programming with MicroPython** using a custom library ecosystem. Every project follows a clean, beginner-friendly structure with real hardware and real output.

---

## 📦 Custom Library Reference

This curriculum uses a set of simplified custom libraries instead of raw MicroPython — so you can focus on **logic, not low-level setup**.

| Library | Import Example | What It Does |
|---------|---------------|--------------|
| `digital` | `from digital import pinMode, digitalWrite, OUTPUT` | Control digital pins — read buttons, drive LEDs, buzzers |
| `analog` | `from analog import analogPin, analogRead` | Read analog sensors — LDR, soil, potentiometer, rain |
| `oled` | `from oled import OLED` | Drive 128×64 I2C OLED display |
| `wifi` | `import wifi` | Connect ESP32 to a Wi-Fi network |
| `adafruitIO` | `import adafruitIO` | Send/receive data via Adafruit IO MQTT cloud |
| `thingspeak` | `from thingspeak import ThingSpeak` | All-in-one WiFi + analog + digital + ThingSpeak upload library |
| `systemio` | `from systemio import run` | Safe program runner with cleanup support |

### 🔧 Program Structure (Every Project)

All projects follow this standard pattern:

```python
def setup():
    # Initialize pins and devices once

def main():
    setup()
    while True:
        # Repeat forever — your main logic here

def cleanup():
    # Turn off everything safely on exit

run(main, cleanup)   # systemio handles safe execution
```

### 📘 Key Function Reference

**`digital` module**

| Function | Usage | Description |
|----------|-------|-------------|
| `pinMode(pin, mode)` | `pinMode(2, OUTPUT)` | Set pin as INPUT / OUTPUT / INPUT_PULLUP |
| `digitalWrite(pin, val)` | `digitalWrite(2, 1)` | Write HIGH (1) or LOW (0) to a pin |
| `digitalRead(pin)` | `digitalRead(4)` | Read 0 or 1 from a digital pin |
| `pwmSetup(pin, freq)` | `pwmSetup(4, freq=1000)` | Set up PWM on a pin |
| `pwmWrite(pin, duty)` | `pwmWrite(4, 512)` | Write PWM duty (0–1023) |
| `pwmStop(pin)` | `pwmStop(4)` | Stop PWM output |

**`analog` module**

| Function | Usage | Description |
|----------|-------|-------------|
| `analogPin(pin)` | `analogPin(34)` | Initialize an analog input pin |
| `analogRead(pin)` | `analogRead(34)` | Read raw ADC value (0–4095) |
| `analogSmooth(pin, window)` | `analogSmooth(34, window=12)` | Averaged reading to reduce noise |
| `analogPercent(pin)` | `analogPercent(34)` | Read value as percentage (0–100%) |
| `analogThreshold(pin, val, samples)` | `analogThreshold(34, 2000, samples=5)` | Returns True if reading exceeds threshold |
| `mapValue(val, in_min, in_max, out_min, out_max)` | `mapValue(raw, 0, 4095, 0, 1023)` | Remap a value from one range to another |

**`oled` module**

| Function | Usage | Description |
|----------|-------|-------------|
| `OLED(scl, sda)` | `oled = OLED(scl=22, sda=21)` | Create OLED object on I2C pins |
| `oled.clear()` | `oled.clear()` | Clear the display buffer |
| `oled.text(str, x, y)` | `oled.text("Hello", 0, 0)` | Write text at position (x, y) |
| `oled.line(x0, y0, x1, y1)` | `oled.line(0, 12, 128, 12)` | Draw a horizontal/vertical line |
| `oled.show()` | `oled.show()` | Push buffer to screen |

---

## 📋 Project List

| # | Project Name | Category | Hardware Used |
|---|-------------|----------|---------------|
| 1 | LED Blink | Digital Output | LED |
| 2 | Button-Controlled LED | Digital Input/Output | LED, Push Button |
| 3 | 4-LED Chaser Pattern | Digital Output | 4× LEDs |
| 4 | Soil Moisture Monitor | Analog Sensor | Soil Sensor |
| 5 | Automatic Street Light (LDR) | Analog + Digital | LDR, LED |
| 6 | OLED Name Display | Display | OLED 128×64 |
| 7 | Object / Visitor Counter | Display + Sensor | OLED, IR Sensor |
| 9 | Air Quality Monitor (IoT) | IoT / Cloud | MQ-3 Gas Sensor, Wi-Fi, ThingSpeak |
| 10 | IoT Home Automation | IoT / Cloud | Wi-Fi, Adafruit IO, Relays |
| 11 | Temperature & Humidity Monitor (IoT) | IoT / Cloud | DHT11, Wi-Fi, ThingSpeak |
| 12 | Robot LED Indicator | Digital / Robot | LEDs, Buttons |
| 13 | Traffic Light Controller | Digital Output | 3× LEDs |
| 14 | Police Siren Light | Digital Output | Red & Blue LEDs |
| 15 | Touch Sensor Light Toggle | Digital Input | Touch Sensor, LED |
| 16 | PWM Brightness Controller | PWM + Analog | Potentiometer, LED |
| 17 | Smart Street Light | Analog Threshold | LDR/Sensor, LED |
| 18 | Fire Alarm Robot | Analog + Motor | Flame Sensor, Motors, Buzzer |
| 19 | Rain Detection System | Analog + PWM | Rain Sensor, Servo, Buzzer |

---

## 🔵 Project 1 — LED Blink

> **Concept:** Turn an LED ON and OFF repeatedly — the "Hello World" of hardware.

**Hardware:** LED on GPIO 2

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LED = 2

def setup():
    pinMode(LED, OUTPUT)

def main():
    setup()
    print("LED Blink Started")
    while True:
        digitalWrite(LED, 1)
        print("ON")
        time.sleep(1)
        digitalWrite(LED, 0)
        print("OFF")
        time.sleep(1)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

**What You Learn:** `pinMode`, `digitalWrite`, `time.sleep`, program loop structure

---

## 🔵 Project 2 — Button-Controlled LED

> **Concept:** Read a push button and control an LED based on the button state.

**Hardware:** LED → GPIO 2 | Button → GPIO 4

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT_PULLUP, OUTPUT
from systemio import run
import time

LED = 2
BTN = 4

def setup():
    pinMode(LED, OUTPUT)
    pinMode(BTN, INPUT_PULLUP)

def main():
    setup()
    print("Button LED Ready")
    while True:
        digitalWrite(LED, not digitalRead(BTN))
        time.sleep(0.01)

def cleanup():
    digitalWrite(LED, 0)
    print("LED OFF — Safe Exit")

run(main, cleanup)
```

**What You Learn:** `digitalRead`, `INPUT_PULLUP`, inverting a button signal

---

## 🔵 Project 3 — 4-LED Chaser Pattern

> **Concept:** Light up 4 LEDs one at a time in a forward-then-reverse chase pattern.

**Hardware:** 4 LEDs on GPIO 2, 4, 5, 18

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LEDS = [2, 4, 5, 18]

def setup():
    for led in LEDS:
        pinMode(led, OUTPUT)
        digitalWrite(led, 0)

def main():
    setup()
    print("LED Chaser Started")
    while True:
        for led in LEDS:
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)
        for led in reversed(LEDS):
            digitalWrite(led, 1)
            time.sleep(0.2)
            digitalWrite(led, 0)

def cleanup():
    for led in LEDS:
        digitalWrite(led, 0)
    print("All LEDs OFF — Safe Exit")

run(main, cleanup)
```

**What You Learn:** Looping over a list of pins, `reversed()`, pattern sequencing

---

## 🟢 Project 4 — Soil Moisture Monitor

> **Concept:** Read a soil moisture sensor and display its status on the serial monitor.

**Hardware:** Soil moisture sensor → GPIO 34 (ADC pin)

```python
from analog import analogPin, analogSmooth
from systemio import run
import time

SOIL_PIN = 34

def setup():
    analogPin(SOIL_PIN)

def main():
    setup()
    print("Soil Moisture Monitor")
    while True:
        value = analogSmooth(SOIL_PIN, window=12)
        moisture = int((4095 - value) * 100 / 4095)

        if moisture < 30:
            status = "DRY ⚠️"
        elif moisture < 70:
            status = "MOIST 🌱"
        else:
            status = "WET 💧"

        print(f"Soil Moisture: {moisture:3d}%   Status: {status}")
        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

**What You Learn:** `analogSmooth`, sensor value mapping, conditional status display

---

## 🟢 Project 5 — Automatic Street Light (LDR)

> **Concept:** Automatically turn an LED ON when it gets dark, using a light sensor.

**Hardware:** LDR → GPIO 34 | LED → GPIO 4

```python
from analog import analogPin, analogThreshold
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

LDR_PIN   = 34
LED_PIN   = 4
THRESHOLD = 2000   # Adjust based on your LDR readings

def setup():
    analogPin(LDR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print(f"LDR Threshold Alert - ADC > {THRESHOLD}")
    while True:
        bright = analogThreshold(LDR_PIN, THRESHOLD, samples=5)
        digitalWrite(LED_PIN, 1 if bright else 0)
        print("BRIGHT ☀️" if bright else "DARK 🌙", end="\r")
        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

**What You Learn:** `analogThreshold`, threshold-based automation, LDR behaviour

---

## 🟣 Project 6 — OLED Name Display

> **Concept:** Display custom text on a 128×64 OLED screen using I2C communication.

**Hardware:** OLED Display → SCL: GPIO 22, SDA: GPIO 21

```python
from oled import OLED
from systemio import run
import time

def main():
    oled = OLED(scl=22, sda=21)
    oled.clear()
    oled.text("Hello, World!", 0, 0)
    oled.text("MicroPython", 16, 20)
    oled.text(" Ready", 16, 40)
    oled.show()
    print("Display updated")
    while True:
        time.sleep(1)

def cleanup():
    print("Stopped")

run(main, cleanup)
```

> 💡 **Try It:** Replace `"Hello, World!"` with your own name!

**What You Learn:** OLED I2C setup, `oled.text()`, `oled.show()`, coordinate system

---

## 🟣 Project 7 — Object / Visitor Counter

> **Concept:** Count objects passing an IR sensor and display the live count on OLED.

**Hardware:** IR Sensor → GPIO 5 | OLED → SCL: 22, SDA: 21

```python
from oled import OLED
from digital import pinMode, digitalRead, INPUT_PULLUP
from systemio import run
import time

IRSENSOR_PIN = 5
count = 0

def main():
    global count
    oled     = OLED(scl=22, sda=21)
    last_btn = 1
    pinMode(IRSENSOR_PIN, INPUT_PULLUP)

    while True:
        btn = digitalRead(IRSENSOR_PIN)
        if last_btn == 1 and btn == 0:
            count += 1
        last_btn = btn

        oled.clear()
        oled.text("Visitor Counter", 0, 0)
        oled.line(0, 12, 128, 12)
        oled.text("Press count:", 0, 24)
        oled.text(str(count), 56, 40)
        oled.show()
        time.sleep(0.05)

def cleanup():
    print("Final count:", count)

run(main, cleanup)
```

**What You Learn:** Edge detection (last vs current state), `global` variables, OLED live updates

---

## 📡 Project 9 — Air Quality Monitor (IoT with ThingSpeak)

> **Concept:** Read an MQ-3 gas/air quality sensor and upload live readings to ThingSpeak cloud every 15 seconds. An LED turns ON when air quality drops below a safe level.

**Hardware:** MQ-3 Gas Sensor → GPIO 34 | Status LED → GPIO 4

> ⚠️ **Required libraries:** `thingspeak.py`, `systemio.py`
> Upload `thingspeak.py` to your ESP32 — it handles WiFi, analog reading, and ThingSpeak upload all in one.

```python
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
```

> 💡 **ThingSpeak Dashboard:** Log in to [thingspeak.com](https://thingspeak.com) → open your channel → Field 1 shows a live air quality graph updated every 15 seconds.

**ThingSpeak Channel Fields:**

| Field | Data | Unit |
|-------|------|------|
| Field 1 | Air Quality Level | % |

**What You Learn:** IoT sensor upload, `ThingSpeak` library, `analog_average_percent`, cloud dashboards, WiFi auto-reconnect

---

## 🌐 Project 10 — IoT Home Automation (Adafruit IO)

> **Concept:** Control home devices remotely through the cloud using Wi-Fi and MQTT.

**Hardware:** Wi-Fi, Relay modules on GPIO 12, 13, 14 | Smoke sensor → GPIO 34

```python
import wifi
import time
import adafruitIO

SMOKE = 34
wifi.setWiFi("YOUR_WIFI", "YOUR_PASSWORD")
wifi.connect()

io = adafruitIO.AdafruitIO("IOName", "YOUR_AIO_KEY")
io.addDevice("light",  12)
io.addDevice("light1", 13)
io.addDevice("light2", 14)
io.addAnalogSensor("sensor", SMOKE)
io.begin()

print("System Ready")

while True:
    io.run()          # MQTT + analog send
    wifi.keepAlive()  # WiFi auto reconnect
    time.sleep_ms(100)
```

> ⚠️ Replace `"YOUR_WIFI"`, `"YOUR_PASSWORD"`, and `"YOUR_AIO_KEY"` with your actual credentials before running.

**What You Learn:** IoT concepts, MQTT protocol, Wi-Fi connectivity, cloud dashboards

---

## 🌡️ Project 11 — Temperature & Humidity Monitor (IoT with ThingSpeak)

> **Concept:** Read temperature and humidity from a DHT11 sensor and upload both values to ThingSpeak cloud. An LED blinks every time data is successfully sent.

**Hardware:** DHT11 Sensor → GPIO 25 | Status LED → GPIO 2

> ⚠️ **Required libraries:** `thingspeak.py`, `systemio.py`
> The DHT11 driver (`dht`) is built into MicroPython — no extra file needed.

```python
from thingspeak import ThingSpeak
from systemio   import run
from machine    import Pin
import dht
import time

WIFI_SSID     = "XXXX"
WIFI_PASSWORD = "XXXX@321#"
TS_WRITE_KEY  = "ULKKQJAZKWWLCPELXK"

DHT_PIN = 25
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
```

> 💡 **ThingSpeak Dashboard:** Log in to [thingspeak.com](https://thingspeak.com) → open your channel → Field 1 shows Temperature, Field 2 shows Humidity as live graphs.

**ThingSpeak Channel Fields:**

| Field | Data | Unit |
|-------|------|------|
| Field 1 | Temperature | °C |
| Field 2 | Humidity | % |

**Wiring:**

| DHT11 Pin | ESP32 GPIO |
|-----------|-----------|
| VCC | 3.3V |
| DATA | GPIO 25 |
| GND | GND |
| (Add 10kΩ pull-up resistor between DATA and VCC) | |

**What You Learn:** DHT11 sensor, `dht` built-in module, dual-field ThingSpeak upload, exception handling with `try/except`, IoT data logging

---

## 🤖 Project 12 — Robot LED Indicator

> **Concept:** Simulate robot turn indicators — LEFT and RIGHT buttons trigger different LED blink patterns (Moving / Idle / Warning modes).

**Hardware:** Left Button → GPIO 34 | Right Button → GPIO 35 | Left LEDs → 21, 18, 19 | Right LEDs → 13, 12, 14

```python
from digital import *
from systemio import run
import time

LEFT_BTN  = 34
RIGHT_BTN = 35
LEFT_LEDS  = [21, 18, 19]
RIGHT_LEDS = [13, 12, 14]

def setup():
    pinMode(LEFT_BTN, INPUT_PULLUP)
    pinMode(RIGHT_BTN, INPUT_PULLUP)
    for led in LEFT_LEDS + RIGHT_LEDS:
        pinMode(led, OUTPUT)

def leds_write(leds, state):
    for led in leds:
        digitalWrite(led, state)

def blink_group(leds, on_time, off_time):
    leds_write(leds, 1); time.sleep(on_time)
    leds_write(leds, 0); time.sleep(off_time)

def main():
    setup()
    print("Left / Right Indicator")
    while True:
        left_pressed  = digitalRead(LEFT_BTN)  == 0
        right_pressed = digitalRead(RIGHT_BTN) == 0

        if left_pressed:
            for _ in range(5):  blink_group(LEFT_LEDS, 0.2, 0.2)  # Moving
            for _ in range(3):  blink_group(LEFT_LEDS, 0.8, 0.8)  # Idle
            for _ in range(10): blink_group(LEFT_LEDS, 0.05, 0.05) # Warning
        elif right_pressed:
            for _ in range(5):  blink_group(RIGHT_LEDS, 0.2, 0.2)
            for _ in range(3):  blink_group(RIGHT_LEDS, 0.8, 0.8)
            for _ in range(10): blink_group(RIGHT_LEDS, 0.05, 0.05)
        else:
            leds_write(LEFT_LEDS, 0)
            leds_write(RIGHT_LEDS, 0)

        time.sleep(0.01)

def cleanup():
    leds_write(LEFT_LEDS, 0)
    leds_write(RIGHT_LEDS, 0)

run(main, cleanup)
```

**What You Learn:** Helper functions, blink patterns, multi-LED groups, robot logic

---

## 🚦 Project 13 — Traffic Light Controller

> **Concept:** Simulate a real traffic light sequence — RED → YELLOW → GREEN → YELLOW.

**Hardware:** Red LED → GPIO 15 | Yellow LED → GPIO 4 | Green LED → GPIO 25

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_PIN    = 15
YELLOW_PIN = 4
GREEN_PIN  = 25
LIGHTS = [RED_PIN, YELLOW_PIN, GREEN_PIN]

def setup():
    for pin in LIGHTS:
        pinMode(pin, OUTPUT)
        digitalWrite(pin, 0)

def set_light(red, yellow, green):
    digitalWrite(RED_PIN, red)
    digitalWrite(YELLOW_PIN, yellow)
    digitalWrite(GREEN_PIN, green)

def main():
    setup()
    print("Traffic Light Started")
    while True:
        print("RED");    set_light(1, 0, 0); time.sleep(3)
        print("YELLOW"); set_light(0, 1, 0); time.sleep(1)
        print("GREEN");  set_light(0, 0, 1); time.sleep(3)
        print("YELLOW"); set_light(0, 1, 0); time.sleep(1)

def cleanup():
    for pin in LIGHTS:
        digitalWrite(pin, 0)
    print("All lights OFF")

run(main, cleanup)
```

**What You Learn:** Multi-pin control, timed sequences, helper functions

---

## 🚨 Project 14 — Police Siren Light

> **Concept:** Alternate RED and BLUE LEDs in three phases — individual flash, then fast alternating siren effect.

**Hardware:** Red LED → GPIO 12 | Blue LED → GPIO 13

```python
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

RED_LED  = 12
BLUE_LED = 13

def setup():
    pinMode(RED_LED, OUTPUT)
    pinMode(BLUE_LED, OUTPUT)

def main():
    setup()
    print("Police Siren Light Started")
    while True:
        for i in range(5):     # Red flashes
            digitalWrite(RED_LED, 1); time.sleep(0.1)
            digitalWrite(RED_LED, 0); time.sleep(0.1)
        for i in range(5):     # Blue flashes
            digitalWrite(BLUE_LED, 1); time.sleep(0.1)
            digitalWrite(BLUE_LED, 0); time.sleep(0.1)
        for i in range(20):    # Fast alternating
            digitalWrite(RED_LED, 1); digitalWrite(BLUE_LED, 0); time.sleep(0.05)
            digitalWrite(RED_LED, 0); digitalWrite(BLUE_LED, 1); time.sleep(0.05)

def cleanup():
    digitalWrite(RED_LED, 0)
    digitalWrite(BLUE_LED, 0)

run(main, cleanup)
```

**What You Learn:** Multi-phase loops, alternating outputs, timing effects

---

## 👆 Project 15 — Touch Sensor Light Toggle

> **Concept:** Touch a sensor to toggle an LED ON or OFF — like a smart touch switch.

**Hardware:** LED → GPIO 4 | Touch Sensor → GPIO 5

```python
from digital import pinMode, digitalWrite, digitalRead, INPUT, OUTPUT
from systemio import run
import time

LED_PIN   = 4
TOUCH_PIN = 5

def setup():
    pinMode(LED_PIN, OUTPUT)
    pinMode(TOUCH_PIN, INPUT)

def main():
    setup()
    led_state  = 0
    last_touch = 0
    print("Touch Sensor Light Started")

    while True:
        touch = digitalRead(TOUCH_PIN)
        if last_touch == 0 and touch == 1:
            led_state = not led_state
            digitalWrite(LED_PIN, led_state)
            print("LED:", "ON" if led_state else "OFF")
        last_touch = touch
        time.sleep(0.05)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

**What You Learn:** Toggle logic, rising-edge detection, state variables

---

## 💡 Project 16 — PWM LED Brightness Controller

> **Concept:** Turn a potentiometer to smoothly control LED brightness using PWM.

**Hardware:** Potentiometer → GPIO 34 | LED → GPIO 4

```python
from analog import analogPin, analogRead, mapValue
from digital import pwmSetup, pwmWrite, pwmStop
from systemio import run
import time

POT_PIN = 34
LED_PIN = 4

def setup():
    analogPin(POT_PIN)
    pwmSetup(LED_PIN, freq=1000)

def main():
    setup()
    print("Pot → LED Brightness")
    while True:
        raw  = analogRead(POT_PIN)               # 0 – 4095
        duty = mapValue(raw, 0, 4095, 0, 1023)   # map to PWM range
        pwmWrite(LED_PIN, duty)
        print(f"ADC: {raw}  →  PWM Duty: {duty}")
        time.sleep(0.05)

def cleanup():
    pwmStop(LED_PIN)

run(main, cleanup)
```

**What You Learn:** PWM signals, `mapValue`, analog-to-PWM conversion

---

## 🌃 Project 17 — Smart Street Light

> **Concept:** Automatically switch a street light based on ambient light threshold.

**Hardware:** Light/Ambient Sensor → GPIO 34 | LED → GPIO 4

```python
from analog import analogPin, analogThreshold
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

SENSOR_PIN = 34
LED_PIN    = 4
THRESHOLD  = 2000

def setup():
    analogPin(SENSOR_PIN)
    pinMode(LED_PIN, OUTPUT)

def main():
    setup()
    print(f"Threshold Alert — trigger at ADC > {THRESHOLD}")
    while True:
        triggered = analogThreshold(SENSOR_PIN, THRESHOLD, samples=5)
        digitalWrite(LED_PIN, 1 if triggered else 0)
        print("ALERT!" if triggered else "Normal", end="\r")
        time.sleep(0.2)

def cleanup():
    digitalWrite(LED_PIN, 0)

run(main, cleanup)
```

**What You Learn:** Real-world automation logic, threshold tuning, sensor sampling

---

## 🔥 Project 18 — Fire Alarm Robot

> **Concept:** A robot that moves forward in safe conditions, but stops and sounds an alarm when fire is detected.

**Hardware:** Flame Sensor → GPIO 34 | Left Motor → GPIO 12, 13 | Right Motor → GPIO 2, 4 | Buzzer → GPIO 14

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, OUTPUT
from systemio import run
import time

FLAME_PIN  = 34
FIRE_LIMIT = 30
LEFT_MOTOR_1 = 12;  LEFT_MOTOR_2  = 13
RIGHT_MOTOR_1 = 2;  RIGHT_MOTOR_2 = 4
BUZZER_PIN = 14

def setup():
    analogPin(FLAME_PIN)
    for pin in [LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2, BUZZER_PIN]:
        pinMode(pin, OUTPUT)

def move_forward():
    digitalWrite(LEFT_MOTOR_1, 1);  digitalWrite(LEFT_MOTOR_2, 0)
    digitalWrite(RIGHT_MOTOR_1, 1); digitalWrite(RIGHT_MOTOR_2, 0)

def stop_robot():
    for pin in [LEFT_MOTOR_1, LEFT_MOTOR_2, RIGHT_MOTOR_1, RIGHT_MOTOR_2]:
        digitalWrite(pin, 0)

def main():
    setup()
    print("Fire Alarm Robot Started")
    while True:
        fire_level = 100 - analogPercent(FLAME_PIN)
        print("Fire Level:", fire_level, "%")
        if fire_level > FIRE_LIMIT:
            print("🔥 FIRE DETECTED!")
            stop_robot()
            digitalWrite(BUZZER_PIN, 1)
        else:
            print("✅ Area Safe")
            digitalWrite(BUZZER_PIN, 0)
            move_forward()
        time.sleep(0.2)

def cleanup():
    stop_robot()
    digitalWrite(BUZZER_PIN, 0)

run(main, cleanup)
```

**What You Learn:** `analogPercent`, motor control, multi-actuator logic, safety thresholds

---

## 🌧️ Project 19 — Rain Detection System

> **Concept:** Detect rain with a sensor, sound a buzzer alarm, and move a servo motor to close/open a cover automatically.

**Hardware:** Rain Sensor → GPIO 34 | Buzzer → GPIO 14 | Servo Motor → GPIO 13

```python
from analog import analogPin, analogPercent
from digital import pinMode, digitalWrite, pwmSetup, pwmWrite, pwmStop, OUTPUT
from systemio import run
import time

RAIN_PIN   = 34
BUZZER_PIN = 14
SERVO_PIN  = 13
RAIN_LIMIT = 30     # % above this = rain detected
ANGLE_RAIN = 120    # degrees — cover CLOSED
ANGLE_DRY  = 30     # degrees — cover OPEN

def angle_to_duty(angle):
    duty = int(26 + (angle / 180) * 102)
    return max(26, min(128, duty))

def servo_move(angle):
    pwmWrite(SERVO_PIN, angle_to_duty(angle))
    print(f"[SERVO] Moving to {angle}°")

def siren():
    for _ in range(3):
        digitalWrite(BUZZER_PIN, 1); time.sleep_ms(100)
        digitalWrite(BUZZER_PIN, 0); time.sleep_ms(100)

def setup():
    analogPin(RAIN_PIN)
    pinMode(BUZZER_PIN, OUTPUT)
    digitalWrite(BUZZER_PIN, 0)
    pwmSetup(SERVO_PIN, freq=50)
    servo_move(ANGLE_DRY)

def main():
    setup()
    prev_state = None
    while True:
        rain = 100 - analogPercent(RAIN_PIN)
        if rain > RAIN_LIMIT:
            if prev_state != "RAIN":
                servo_move(ANGLE_RAIN)
                prev_state = "RAIN"
            siren()
            print(f"[SENSOR] Rain: {rain:3d}%  Status: RAIN DETECTED ☔")
        else:
            if prev_state != "DRY":
                servo_move(ANGLE_DRY)
                prev_state = "DRY"
            digitalWrite(BUZZER_PIN, 0)
            print(f"[SENSOR] Rain: {rain:3d}%  Status: NO RAIN ☀")
        time.sleep(1)

def cleanup():
    servo_move(ANGLE_DRY)
    time.sleep_ms(500)
    pwmStop(SERVO_PIN)
    digitalWrite(BUZZER_PIN, 0)
    print("\n[CLEANUP] System stopped safely")

run(main, cleanup)
```

**What You Learn:** Servo control with PWM, `angle_to_duty` mapping, state-change logic, multi-actuator systems

---

## 🛠️ Hardware Setup Guide

### ESP32 ADC Pins (for Analog Sensors)
> Only certain GPIO pins support ADC on ESP32. Safe pins: **32, 33, 34, 35, 36, 39**

### I2C Pins (for OLED)
| Signal | Default GPIO |
|--------|-------------|
| SCL | 22 |
| SDA | 21 |

### Recommended Pin Summary

| Component | GPIO |
|-----------|------|
| Onboard LED | 2 |
| General LED output | 4, 5, 25 |
| Button / Sensor input | 4, 5, 35 |
| Analog sensors | 34 |
| Motor driver pins | 12, 13, 2, 4 |
| Buzzer | 14 |
| Servo | 13 |
| OLED SCL / SDA | 22 / 21 |

---

## 🚀 Getting Started

### 1. Flash MicroPython to your ESP32
Download from: [micropython.org/download/ESP32_GENERIC](https://micropython.org/download/ESP32_GENERIC/)

### 2. Install Thonny IDE
Download from: [thonny.org](https://thonny.org/) — beginner-friendly editor with built-in ESP32 support.

### 3. Upload the Custom Libraries
Copy these files to your ESP32 using Thonny (Files → Upload):
```
digital.py
analog.py
oled.py
systemio.py
wifi.py
adafruitIO.py
thingspeak.py    ← required for Projects 9 and 11
```

### 4. Run a Project
- Open any project `.py` file in Thonny
- Click ▶ **Run** or press `F5`
- Watch the Serial Monitor for output

---

## 📚 Learning Path (Beginner → Advanced)

```
Week 1 → Projects 1, 2, 3       (Digital I/O basics)
Week 2 → Projects 4, 5, 17      (Analog sensors)
Week 3 → Projects 6, 7          (OLED display)
Week 4 → Projects 13, 14, 15    (Real-world controls)
Week 5 → Projects 16, 18, 19    (PWM + Motors + Servo)
Week 6 → Projects 9, 11         (IoT + ThingSpeak cloud)
Week 7 → Project 10             (IoT + Adafruit IO cloud)
```

---

## 🤝 Contributing

1. Fork this repository
2. Add your project in a new folder: `ProjectXX_Name/`
3. Include: `main.py` + a short description comment at the top
4. Open a Pull Request

---

> *"Tell me and I forget. Teach me and I remember. Involve me and I learn."* — Benjamin Franklin
