import os
import struct
import sys
import math
import time

def play_alarm_tone():
    # Parameters for the alarm sound (800Hz tone, 16-bit, 44.1kHz)
    sample_rate = 44100
    frequency = 800.0  # Pitch in Hz
    duration = 0.4     # Beep duration in seconds

    num_samples = int(sample_rate * duration)

    # Generate PCM 16-bit audio data (sine wave)
    samples = bytearray()
    for i in range(num_samples):
        # Calculate sine wave amplitude
        sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.extend(struct.pack('<h', sample))

    # Write audio stream to a raw file
    raw_audio_path = "/tmp/alarm_tone.raw"
    with open(raw_audio_path, "wb") as f:
        f.write(samples)

    # Beep 6 times using native ALSA 'aplay' or PipeWire 'pw-cat'
    for _ in range(6):
        # Try ALSA raw playback
        cmd = f"aplay -q -f S16_LE -r {sample_rate} -c 1 {raw_audio_path} &>/dev/null"
        if os.system(cmd) != 0:
            # Fallback for pure PipeWire setups
            os.system(f"pw-cat -p --format=s16 --rate={sample_rate} --channels=1 {raw_audio_path} &>/dev/null")
        time.sleep(0.15)

    if os.path.exists(raw_audio_path):
        os.remove(raw_audio_path)

# Force prompt explicitly
sys.stdout.write("Enter countdown duration (hh:mm:ss): ")
sys.stdout.flush()
time_str = sys.stdin.readline().strip()

try:
    hours, minutes, seconds = map(int, time_str.split(":"))
    total_seconds = hours * 3600 + minutes * 60 + seconds
except Exception as e:
    print(f"Error parsing time: {e}")
    sys.exit(1)

print("\nCountdown started...")

while total_seconds > 0:
    hrs, remainder = divmod(total_seconds, 3600)
    mins, secs = divmod(remainder, 60)
    sys.stdout.write(f"\rTime remaining: {hrs:02d}:{mins:02d}:{secs:02d}")
    sys.stdout.flush()
    time.sleep(1)
    total_seconds -= 1

print("\n\nTime's up!")
play_alarm_tone()
