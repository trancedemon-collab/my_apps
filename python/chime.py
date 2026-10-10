import math
import os
import select
import struct
import sys
import termios
import time
import tty

# --- Audio Setup ---
RAW_AUDIO_PATH = "/tmp/chime_tone.raw"


def generate_chime_sound():
    """Generates a pleasant 600Hz chime tone PCM raw audio file."""
    sample_rate = 44100
    duration = 0.25  # Duration of a single chime beep
    frequency = 600.0  # Warm chime pitch

    num_samples = int(sample_rate * duration)
    samples = bytearray()
    for i in range(num_samples):
        # Apply exponential decay so the beep sounds like a soft chime instead of a harsh tone
        envelope = math.exp(-3.0 * (i / num_samples))
        sample = int(
            32767
            * math.sin(2 * math.pi * frequency * i / sample_rate)
            * envelope
        )
        samples.extend(struct.pack("<h", sample))

    with open(RAW_AUDIO_PATH, "wb") as f:
        f.write(samples)


def play_chime(beep_count):
    """Plays the generated chime audio repeatedly based on the current hour."""
    if not os.path.exists(RAW_AUDIO_PATH):
        generate_chime_sound()

    print(f"\n[CHIME] Top of the hour! Playing {beep_count} beep(s)...")

    for _ in range(beep_count):
        cmd_aplay = (
            f"aplay -q -f S16_LE -r 44100 -c 1 {RAW_AUDIO_PATH} &>/dev/null"
        )
        if os.system(cmd_aplay) != 0:
            os.system(
                "pw-cat -p --format=s16 --rate=44100 --channels=1"
                f" {RAW_AUDIO_PATH} &>/dev/null"
            )
        time.sleep(0.4)  # Pause between chime beeps


def get_key_press():
    """Non-blocking key check using select."""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1).lower()
    return None


def run_hourly_chime():
    print("=" * 45)
    print("      HOURLY CHIME CLOCK (12-Hour Format)")
    print("=" * 45)
    print("Running in background... Press [Q] at any time to quit.\n")

    generate_chime_sound()
    last_chimed_hour = -1

    old_settings = termios.tcgetattr(sys.stdin)

    try:
        tty.setcbreak(sys.stdin.fileno())

        while True:
            now = time.localtime()

            # Check if we are at the top of an hour (minute 0, second 0)
            if now.tm_min == 0 and now.tm_sec == 0:
                if last_chimed_hour != now.tm_hour:
                    # Convert 24-hour time (0-23) to 12-hour format (1-12)
                    chime_count = now.tm_hour % 12
                    if chime_count == 0:
                        chime_count = 12

                    play_chime(chime_count)
                    last_chimed_hour = now.tm_hour

            # Display real-time clock status line
            time_str = time.strftime("%I:%M:%S %p", now)
            sys.stdout.write(f"\rCurrent Time: {time_str} | Status: Active ")
            sys.stdout.flush()

            # Listen for quit keypress 4 times a second (negligible CPU usage)
            for _ in range(4):
                key = get_key_press()
                if key == "q":
                    sys.stdout.write("\n\nExiting Hourly Chime... Goodbye!\n")
                    return
                time.sleep(0.25)

    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        if os.path.exists(RAW_AUDIO_PATH):
            os.remove(RAW_AUDIO_PATH)


if __name__ == "__main__":
    run_hourly_chime()