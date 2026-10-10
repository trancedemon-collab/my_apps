import glob
import math
import os
import select
import struct
import subprocess
import sys
import termios
import time
import tty

def play_tone(frequency, volume_factor=0.6, duration=0.12):
    """Synthesizes and plays a clean PCM sine wave buzz with adjustable volume."""
    sample_rate = 44100
    num_samples = int(sample_rate * duration)
    samples = bytearray()

    # Scale 16-bit amplitude by volume (max 32767)
    peak_amplitude = int(32767 * max(0.01, min(1.0, volume_factor)))

    for i in range(num_samples):
        envelope = math.exp(-3.0 * (i / num_samples))
        val = int(peak_amplitude * math.sin(2 * math.pi * frequency * i / sample_rate) * envelope)
        samples.extend(struct.pack("<h", val))

    try:
        proc = subprocess.Popen(
            ["aplay", "-q", "-f", "S16_LE", "-r", "44100", "-c", "1"],
            stdin=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        proc.communicate(input=samples)
    except FileNotFoundError:
        try:
            proc = subprocess.Popen(
                ["pw-cat", "-p", "--format=s16", "--rate=44100", "--channels=1"],
                stdin=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )
            proc.communicate(input=samples)
        except FileNotFoundError:
            print("\a", end="", flush=True)

def get_cpu_temp():
    """Reads temperature directly from sysfs thermal and hwmon interfaces."""
    sensor_paths = glob.glob("/sys/class/hwmon/hwmon*/temp*_input") + glob.glob(
        "/sys/class/thermal/thermal_zone*/temp"
    )
    for path in sensor_paths:
        try:
            with open(path, "r") as f:
                val = int(f.read().strip())
                if val > 0:
                    return val / 1000.0 if val > 1000 else float(val)
        except (ValueError, IOError):
            continue
    return None

def get_frequency_for_temp(temp):
    """
    Maps 10°C temperature brackets to pitch:
    <30°C: 200 Hz | 30s: 350 Hz | 40s: 500 Hz | 50s: 650 Hz
    60s: 800 Hz   | 70s: 950 Hz | 80s: 1100 Hz | 90s+: 1250 Hz+
    """
    tier = int(temp // 10)
    base_freq = 200.0
    if tier <= 2:
        return base_freq
    return base_freq + ((tier - 2) * 150.0)

def get_dynamic_interval(temp, base_interval):
    """
    Dynamically shortens check duration as temperature rises:
    <60°C: base interval
    >=60°C: 5s
    >=70°C: 2.5s
    >=80°C: 1s (minimum duration)
    """
    interval = base_interval
    if temp >= 60:
        interval = min(interval, 5.0)
    if temp >= 70:
        interval = min(interval, 2.5)
    if temp >= 80:
        interval = min(interval, 1.0)
    return max(1.0, interval)

def get_key_press():
    """Non-blocking key check."""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1).lower()
    return None

def prompt_config():
    print("=" * 55)
    print("              CPU TEMPERATURE MONITOR")
    print("=" * 55)

    # 1. Threshold
    sys.stdout.write("Set threshold limit in °C [Press Enter for No Limit]: ")
    sys.stdout.flush()
    thresh_raw = sys.stdin.readline().strip()
    if thresh_raw == "":
        threshold = None
    else:
        try:
            threshold = float(thresh_raw)
        except ValueError:
            threshold = None

    # 2. Check Delay / Interval
    sys.stdout.write("Check interval in seconds [Press Enter for 10s]: ")
    sys.stdout.flush()
    delay_raw = sys.stdin.readline().strip()
    if delay_raw == "":
        interval = 10.0
    else:
        try:
            interval = float(delay_raw)
        except ValueError:
            interval = 10.0

    # 3. Dynamic Interval
    sys.stdout.write("Enable dynamic interval shortening on high temp (y/n) [Press Enter for y]: ")
    sys.stdout.flush()
    dyn_raw = sys.stdin.readline().strip().lower()
    if dyn_raw == "" or dyn_raw.startswith("y"):
        dynamic_interval = True
    else:
        dynamic_interval = False

    # 4. Volume
    sys.stdout.write("Buzzer volume percentage 1-100 [Press Enter for 60%]: ")
    sys.stdout.flush()
    vol_raw = sys.stdin.readline().strip()
    if vol_raw == "":
        vol_pct = 60.0
    else:
        try:
            vol_pct = float(vol_raw)
        except ValueError:
            vol_pct = 60.0

    volume = vol_pct / 100.0

    print("-" * 55)
    thresh_str = f"{threshold:.1f}°C" if threshold is not None else "None (Always active)"
    dyn_str = "Enabled" if dynamic_interval else "Disabled"
    print(f"Config -> Threshold: {thresh_str} | Base Interval: {interval:.1f}s | Dynamic: {dyn_str} | Volume: {vol_pct:.0f}%")
    print("Press [Q] to quit.\n")
    return threshold, interval, dynamic_interval, volume

def run_monitor():
    if get_cpu_temp() is None:
        print("Error: Could not locate readable temperature sensors in /sys/class/.")
        return

    threshold, interval, dynamic_interval, volume = prompt_config()

    old_settings = termios.tcgetattr(sys.stdin)
    last_check_time = 0
    last_temp = None

    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            now = time.time()
            current_interval = get_dynamic_interval(last_temp, interval) if (dynamic_interval and last_temp is not None) else interval

            if now - last_check_time >= current_interval:
                temp = get_cpu_temp()
                last_check_time = now

                if temp is not None:
                    last_temp = temp
                    current_interval = get_dynamic_interval(temp, interval) if dynamic_interval else interval

                    freq = get_frequency_for_temp(temp)
                    bracket_low = int((temp // 10) * 10)
                    bracket_high = bracket_low + 9

                    should_buzz = (threshold is None) or (temp >= threshold)

                    if should_buzz:
                        sys.stdout.write(
                            f"\rCPU: {temp:.1f}°C [{bracket_low}-{bracket_high}°C] -> Buzzer: {freq:.0f} Hz [ALERT] (Int: {current_interval:.1f}s)   "
                        )
                        sys.stdout.flush()
                        play_tone(freq, volume_factor=volume, duration=0.12)
                    else:
                        sys.stdout.write(
                            f"\rCPU: {temp:.1f}°C | Status: Below {threshold:.0f}°C [SILENT] (Int: {current_interval:.1f}s)                    "
                        )
                        sys.stdout.flush()

            key = get_key_press()
            if key == "q":
                sys.stdout.write("\n\nExiting temperature monitor...\n")
                break

            time.sleep(0.1)

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    run_monitor()
