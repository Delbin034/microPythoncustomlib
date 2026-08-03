# ============================================================
#  thingspeak.py  —  All-in-One ThingSpeak Library for ESP32
#  Integrates: WiFi + Analog + Digital + PWM + Upload
#
#  WHAT THIS LIB DOES
#  ─────────────────────────────────────────────────────────
#  → Connects WiFi automatically on init
#  → Wraps analog.py  : analogPin, analogRead, analogPercent,
#                        analogVoltage, analogAverage
#  → Wraps digital.py : pinMode, digitalWrite, digitalRead,
#                        pwmSetup, pwmWrite, pwmStop
#  → Uploads any field data to ThingSpeak via HTTP GET
#  → Enforces 15s ThingSpeak free-tier limit automatically
#  → Auto-reconnects WiFi if dropped (keep_alive)
#
#  USAGE IN main.py
#  ─────────────────────────────────────────────────────────
#  from thingspeak import ThingSpeak
#
#  ts = ThingSpeak("WRITE_KEY", "WiFi", "Password")
#
#  ts.analog_pin(34)                  # setup ADC
#  ts.digital_out(2)                  # setup LED
#  ts.pwm_out(13, freq=50)            # setup PWM
#
#  val = ts.analog_read(34)           # raw 0-4095
#  pct = ts.analog_percent(34)        # 0-100 %
#  v   = ts.analog_voltage(34)        # 0.0-3.3 V
#  avg = ts.analog_average(34, 10)    # averaged raw
#
#  ts.digital_write(2, 1)             # LED ON
#  state = ts.digital_read(15)        # read button
#  ts.pwm_write(13, 512)              # duty 0-1023
#  ts.pwm_write_percent(13, 75)       # duty as %
#  ts.pwm_stop(13)                    # stop PWM
#
#  ts.send(field1=pct, field2=v)      # upload to ThingSpeak
#  ts.keep_alive()                    # WiFi watchdog
# ============================================================

import socket
import time
from machine import Pin, ADC, PWM

class ThingSpeak:

    HOST     = "api.thingspeak.com"
    PORT     = 80
    INTERVAL = 15          # free-tier minimum seconds between uploads

    def __init__(self, write_key, ssid, password):
        self._key      = write_key
        self._ssid     = ssid
        self._password = password
        self._last_send = time.ticks_ms() - self.INTERVAL * 1000

        # Internal pin stores
        self._adcs = {}
        self._pins = {}
        self._pwms = {}

        # Connect WiFi on init
        self._wifi_connect()

    # ══════════════════════════════════════════════════════
    #  WIFI  (uses wifi.py logic — no import needed)
    # ══════════════════════════════════════════════════════

    def _wifi_connect(self):
        import network
        sta = network.WLAN(network.STA_IF)
        # Radio reset — fixes Internal State Error after soft reboot
        try: sta.disconnect()
        except: pass
        sta.active(False)
        time.sleep_ms(300)
        sta.active(True)
        time.sleep_ms(200)

        if sta.isconnected():
            print("[WiFi] Already connected →", sta.ifconfig()[0])
            return

        print("[WiFi] Connecting to", self._ssid, "...")
        sta.connect(self._ssid, self._password)
        for _ in range(30):
            if sta.isconnected(): break
            time.sleep_ms(500)
            print(".", end="")
        print()

        if sta.isconnected():
            print("[WiFi] Connected →", sta.ifconfig()[0])
        else:
            print("[WiFi] Failed to connect")

    def keep_alive(self):
        """Call in main loop — reconnects WiFi if dropped."""
        import network
        sta = network.WLAN(network.STA_IF)
        if not sta.isconnected():
            print("[WiFi] Lost — reconnecting...")
            self._wifi_connect()

    def is_connected(self):
        import network
        return network.WLAN(network.STA_IF).isconnected()

    # ══════════════════════════════════════════════════════
    #  ANALOG  (wraps analog.py functions)
    # ══════════════════════════════════════════════════════

    def analog_pin(self, pin, attn=None, width=None):
        """Setup ADC pin. Default: 11dB attn (0-3.3V), 12-bit."""
        adc = ADC(Pin(pin))
        adc.atten(attn   if attn  is not None else ADC.ATTN_11DB)
        adc.width(width  if width is not None else ADC.WIDTH_12BIT)
        self._adcs[pin] = adc
        print(f"[ADC]  Pin {pin} configured")

    def analog_read(self, pin):
        """Raw ADC value 0–4095."""
        return self._adcs[pin].read()

    def analog_percent(self, pin):
        """ADC reading as 0–100 %."""
        return int(self.analog_read(pin) / 4095 * 100)

    def analog_voltage(self, pin, vref=3.3):
        """ADC reading as voltage 0.0–3.3 V."""
        return round(self.analog_read(pin) / 4095 * vref, 3)

    def analog_average(self, pin, samples=10):
        """Average of N ADC readings — reduces noise."""
        total = 0
        for _ in range(samples):
            total += self._adcs[pin].read()
            time.sleep_ms(2)
        return total // samples

    def analog_average_percent(self, pin, samples=10):
        """Averaged ADC reading as 0–100 %."""
        return int(self.analog_average(pin, samples) / 4095 * 100)

    def analog_average_voltage(self, pin, samples=10, vref=3.3):
        """Averaged ADC reading as voltage."""
        return round(self.analog_average(pin, samples) / 4095 * vref, 3)

    def map_value(self, x, in_min, in_max, out_min, out_max):
        """Map a value from one range to another (integer output)."""
        if in_max == in_min: return out_min
        result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        return int(max(out_min, min(out_max, result)))

    # ══════════════════════════════════════════════════════
    #  DIGITAL  (wraps digital.py functions)
    # ══════════════════════════════════════════════════════

    def digital_out(self, pin):
        """Configure pin as digital OUTPUT."""
        self._pins[pin] = Pin(pin, Pin.OUT)
        print(f"[GPIO] Pin {pin} → OUTPUT")

    def digital_in(self, pin, pullup=False, pulldown=False):
        """Configure pin as digital INPUT."""
        if pullup:
            self._pins[pin] = Pin(pin, Pin.IN, Pin.PULL_UP)
        elif pulldown:
            self._pins[pin] = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        else:
            self._pins[pin] = Pin(pin, Pin.IN)
        print(f"[GPIO] Pin {pin} → INPUT")

    def digital_write(self, pin, value):
        """Write HIGH(1) or LOW(0) to output pin."""
        self._pins[pin].value(value)

    def digital_read(self, pin):
        """Read current state of a pin — returns 0 or 1."""
        return self._pins[pin].value()

    def toggle(self, pin):
        """Toggle pin state HIGH↔LOW."""
        self._pins[pin].value(not self._pins[pin].value())

    def blink(self, pin, times=3, on_ms=200, off_ms=200):
        """Blink a pin N times."""
        for _ in range(times):
            self._pins[pin].value(1); time.sleep_ms(on_ms)
            self._pins[pin].value(0); time.sleep_ms(off_ms)

    def pulse(self, pin, duration_ms=100):
        """Single HIGH pulse then LOW."""
        self._pins[pin].value(1)
        time.sleep_ms(duration_ms)
        self._pins[pin].value(0)

    # ══════════════════════════════════════════════════════
    #  PWM  (wraps digital.py PWM functions)
    # ══════════════════════════════════════════════════════

    def pwm_out(self, pin, freq=1000):
        """Initialize PWM on pin at given frequency."""
        self._pwms[pin] = PWM(Pin(pin), freq=freq)
        print(f"[PWM]  Pin {pin} → {freq} Hz")

    def pwm_write(self, pin, duty):
        """Set PWM duty cycle 0–1023."""
        self._pwms[pin].duty(duty)

    def pwm_write_percent(self, pin, percent):
        """Set PWM duty as percentage 0–100 %."""
        self._pwms[pin].duty(int(percent / 100 * 1023))

    def pwm_freq(self, pin, freq):
        """Change PWM frequency on the fly."""
        self._pwms[pin].freq(freq)

    def pwm_stop(self, pin):
        """Stop and deinit PWM on pin."""
        if pin in self._pwms:
            self._pwms[pin].deinit()
            del self._pwms[pin]

    # ══════════════════════════════════════════════════════
    #  THINGSPEAK UPLOAD
    # ══════════════════════════════════════════════════════

    def send(self, **fields):
        """
        Upload field values to ThingSpeak.
        Automatically enforces 15s minimum interval.

        Example:
            ts.send(field1=25.3, field2=60, field3=1)

        Returns True on success, False if skipped or failed.
        """
        now = time.ticks_ms()
        remaining = self.INTERVAL - time.ticks_diff(now, self._last_send) // 1000
        if remaining > 0:
            print(f"[TS]   Wait {remaining}s before next send")
            return False

        if not self.is_connected():
            print("[TS]   No WiFi — skipping upload")
            return False

        # Build URL query string
        params  = "&".join(f"{k}={v}" for k, v in fields.items())
        path    = f"/update?api_key={self._key}&{params}"
        request = (
            f"GET {path} HTTP/1.0\r\n"
            f"Host: {self.HOST}\r\n"
            f"Connection: close\r\n\r\n"
        )

        try:
            addr = socket.getaddrinfo(self.HOST, self.PORT)[0][-1]
            s    = socket.socket()
            s.settimeout(8)
            s.connect(addr)
            s.send(request.encode())
            resp  = s.recv(128).decode()
            s.close()
            entry = resp.split("\r\n\r\n")[-1].strip()
            if entry and entry != "0":
                self._last_send = time.ticks_ms()
                print(f"[TS]   Sent OK  entry=#{entry}  fields={fields}")
                return True
            else:
                print("[TS]   Server rejected (entry=0)")
                return False
        except Exception as e:
            print("[TS]   Send error →", e)
            return False

    # ══════════════════════════════════════════════════════
    #  HELPER — stop all outputs safely
    # ══════════════════════════════════════════════════════

    def all_off(self):
        """Turn off all digital outputs and stop all PWM channels."""
        for pin in self._pins:
            try: self._pins[pin].value(0)
            except: pass
        for pin in list(self._pwms.keys()):
            self.pwm_stop(pin)
        print("[Safe] All outputs OFF")
