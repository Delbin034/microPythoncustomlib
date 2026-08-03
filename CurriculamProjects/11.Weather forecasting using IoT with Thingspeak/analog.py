from machine import Pin, ADC, DAC
import time

# ============================================================
#  ESP32 ANALOG I/O LIBRARY
#  Supports: ADC Read, DAC Write, Averaging, Smoothing, Mapping
# ============================================================

_adcs    = {}
_dacs    = {}
_smooth  = {}  # Stores rolling buffers for smoothing

ATTN_0DB   = ADC.ATTN_0DB    # 0–1V
ATTN_2_5DB = ADC.ATTN_2_5DB  # 0–1.34V
ATTN_6DB   = ADC.ATTN_6DB    # 0–2V
ATTN_11DB  = ADC.ATTN_11DB   # 0–3.6V  (most common for full 3.3V range)

WIDTH_9BIT  = ADC.WIDTH_9BIT   # 0–511
WIDTH_10BIT = ADC.WIDTH_10BIT  # 0–1023
WIDTH_11BIT = ADC.WIDTH_11BIT  # 0–2047
WIDTH_12BIT = ADC.WIDTH_12BIT  # 0–4095 (default)

# ---------- ANALOG SETUP ----------

def analogPin(pin, attn=ADC.ATTN_11DB, width=ADC.WIDTH_12BIT):
    """
    Configure an ADC pin.
    attn  : Attenuation level (affects input voltage range).
    width : Bit resolution (9–12 bit).
    """
    adc = ADC(Pin(pin))
    adc.atten(attn)
    adc.width(width)
    _adcs[pin] = adc
    _smooth[pin] = []

# ---------- RAW READ ----------

def analogRead(pin):
    """Return the raw ADC value."""
    return _adcs[pin].read()

# ---------- PERCENT ----------

def analogPercent(pin):
    """Return ADC reading mapped to 0–100%."""
    raw = analogRead(pin)
    return mapValue(raw, 0, 4095, 0, 100)

# ---------- VOLTAGE ----------

def analogVoltage(pin, vref=3.3):
    """Return estimated voltage at the pin (based on vref, default 3.3V)."""
    raw = analogRead(pin)
    return round((raw / 4095.0) * vref, 3)

# ---------- AVERAGE READ ----------

def analogAverage(pin, samples=10):
    """Read the pin N times and return the integer average."""
    total = 0
    for _ in range(samples):
        total += _adcs[pin].read()
        time.sleep_ms(2)
    return total // samples

# ---------- AVERAGE PERCENT ----------

def analogAveragePercent(pin, samples=10):
    """Return averaged ADC reading as 0–100%."""
    avg = analogAverage(pin, samples)
    return mapValue(avg, 0, 4095, 0, 100)

# ---------- SMOOTHED READ ----------

def analogSmooth(pin, window=8):
    """
    Moving-average smoothing. Keeps a rolling window of N readings.
    Call repeatedly in a loop to get a smoothed value.
    """
    _smooth[pin].append(_adcs[pin].read())
    if len(_smooth[pin]) > window:
        _smooth[pin].pop(0)
    return sum(_smooth[pin]) // len(_smooth[pin])

# ---------- MAP ----------

def mapValue(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another (integer output)."""
    if in_max == in_min:
        return out_min
    result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return int(max(out_min, min(out_max, result)))

# ---------- MAP FLOAT ----------

def mapFloat(x, in_min, in_max, out_min, out_max):
    """Map a value from one range to another (float output)."""
    if in_max == in_min:
        return float(out_min)
    result = (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    return float(max(out_min, min(out_max, result)))

# ---------- THRESHOLD ----------

def analogThreshold(pin, threshold, samples=1):
    """Return True if the averaged ADC reading exceeds the raw threshold."""
    if samples > 1:
        val = analogAverage(pin, samples)
    else:
        val = analogRead(pin)
    return val > threshold

# ---------- DAC SETUP ----------

def dacPin(pin):
    """
    Initialize a DAC output.
    ESP32 DAC pins: GPIO 25 and GPIO 26 only.
    """
    _dacs[pin] = DAC(Pin(pin))

# ---------- DAC WRITE ----------

def dacWrite(pin, value):
    """Write a raw value (0–255) to the DAC output."""
    _dacs[pin].write(int(max(0, min(255, value))))

# ---------- DAC WRITE VOLTAGE ----------

def dacWriteVoltage(pin, voltage, vref=3.3):
    """Write a target voltage (0–vref) to the DAC output."""
    value = int((voltage / vref) * 255)
    dacWrite(pin, value)

# ---------- DAC WRITE PERCENT ----------

def dacWritePercent(pin, percent):
    """Write 0–100% as a DAC voltage."""
    value = int((percent / 100.0) * 255)
    dacWrite(pin, value)
