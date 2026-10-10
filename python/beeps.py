import math
import os
import select
import struct
import sys
import termios
import time
import tty


def trigger_single_beep():
    sample_rate = 44100
    duration = 0.35
    frequency = 800.0

    num_samples = int(sample_rate * duration)
    samples = bytearray()
    for i in range(num_samples):
        sample = int(32767 * math.sin(2 * math.pi * frequency * i / sample_rate))
        samples.extend(struct.pack("<h", sample))

    raw_path = "/tmp/interval_beep.raw"
    with open(raw_path, "wb") as f:
        f.write(samples)

    cmd_aplay = f"aplay -q -f S16_LE -r {sample_rate} -c 1 {raw_path} &>/dev/null"
    if os.system(cmd_aplay) != 0:
        os.system(
            f"pw-cat -p --format=s16 --rate={sample_rate} --channels=1 {raw_path} &>/dev/null"
        )

    if os.path.exists(raw_path):
        os.remove(raw_path)


def get_key_press():
    """Non-blocking key check using select."""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1).lower()
    return None


def run_timer_loop():
    while True:
        # Step 1: Standard text input screen
        print("\n" + "=" * 35)
        sys.stdout.write("Enter interval duration (hh:mm:ss) [q to exit]: ")
        sys.stdout.flush()
        time_str = sys.stdin.readline().strip().lower()

        if time_str == "q":
            print("Exiting...")
            break

        try:
            hours, minutes, seconds = map(int, time_str.split(":"))
            interval_seconds = hours * 3600 + minutes * 60 + seconds
            if interval_seconds <= 0:
                raise ValueError
        except Exception:
            print("Invalid input format! Use hh:mm:ss (e.g., 00:05:00)")
            continue

        print("\nControls: [P] Pause/Resume | [R] Reset to Main Screen | [Q] Quit Program\n")

        current_seconds = interval_seconds
        is_paused = False

        # Step 2: Switch terminal to cbreak mode for key detection
        old_settings = termios.tcgetattr(sys.stdin)
        reset_to_main = False

        try:
            tty.setcbreak(sys.stdin.fileno())

            while True:
                # Render countdown status
                hrs, remainder = divmod(current_seconds, 3600)
                mins, secs = divmod(remainder, 60)
                status = " [PAUSED]" if is_paused else "         "
                sys.stdout.write(
                    f"\rRemaining: {hrs:02d}:{mins:02d}:{secs:02d}{status}"
                )
                sys.stdout.flush()

                if not is_paused and current_seconds == 0:
                    trigger_single_beep()
                    current_seconds = interval_seconds
                    continue

                # Check keys 4 times per second (0.25s interval = negligible CPU load)
                clock_ticked = False
                for _ in range(4):
                    key = get_key_press()
                    if key == "q":
                        sys.stdout.write("\n\nExiting...\n")
                        return
                    elif key == "p":
                        is_paused = not is_paused
                        break
                    elif key == "r":
                        sys.stdout.write("\n\nResetting to main screen...\n")
                        reset_to_main = True
                        break

                    time.sleep(0.25)
                    clock_ticked = True

                if reset_to_main:
                    break

                if not is_paused and clock_ticked:
                    current_seconds -= 1

        finally:
            # Restore normal terminal behavior for the next text input
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


if __name__ == "__main__":
    run_timer_loop()
