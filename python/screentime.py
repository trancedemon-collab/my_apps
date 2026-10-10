import os
import sys
import time
import datetime
import dbus

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(SCRIPT_DIR, "screen_time.log")

# Configuration
CHECK_INTERVAL = 1  # seconds between checks
IDLE_THRESHOLD_MS = 60000  # 60 seconds idle before pausing counter


def get_idle_ms():
    """Fetches user idle time in milliseconds from KDE Plasma via DBus."""
    try:
        bus = dbus.SessionBus()
        # Query KDE Idle Detector
        idle_object = bus.get_object(
            "org.kde.kscreenlocker", "/org/kde/kscreenlocker"
        )
        # Fallback check using KIdleTime if screenlocker is not present
        interface = dbus.Interface(idle_object, "org.freedesktop.DBus.Properties")
        # Direct check onorg.freedesktop.ScreenSaver
        ss_object = bus.get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
        return ss_object.GetSessionIdleTime(dbus_interface="org.freedesktop.ScreenSaver")
    except Exception:
        # Generic X11 / Wayland fallback using org.freedesktop.ScreenSaver
        try:
            bus = dbus.SessionBus()
            ss_object = bus.get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
            return int(ss_object.GetSessionIdleTime())
        except Exception:
            return 0  # Assume active if idle time cannot be determined


def load_today_seconds():
    """Reads the log file and resumes today's accumulated seconds if present."""
    today_str = datetime.date.today().isoformat()
    if not os.path.exists(LOG_FILE):
        return 0

    last_matching_seconds = 0
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    date_part, secs_part = parts[0], parts[1]
                    if date_part == today_str:
                        last_matching_seconds = int(secs_part)
    except Exception:
        pass

    return last_matching_seconds


def log_today_seconds(seconds):
    """Logs the current day's accumulated seconds to file."""
    today_str = datetime.date.today().isoformat()
    lines = []
    updated = False

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()

    # Rewrite or update current day entry
    new_lines = []
    for line in lines:
        parts = line.strip().split(",")
        if len(parts) == 2 and parts[0] == today_str:
            new_lines.append(f"{today_str},{seconds}\n")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{today_str},{seconds}\n")

    with open(LOG_FILE, "w") as f:
        f.writelines(new_lines)


def format_hh_mm_ss(seconds):
    """Formats total seconds into HH:MM:SS."""
    return str(datetime.timedelta(seconds=seconds))


def main():
    accumulated_seconds = load_today_seconds()
    last_log_time = time.time()
    current_day = datetime.date.today()

    print(f"Tracking Screen-On Time. [Log: {LOG_FILE}]")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Handle midnight rollover
            if datetime.date.today() != current_day:
                current_day = datetime.date.today()
                accumulated_seconds = 0

            idle_ms = get_idle_ms()

            # Increment only if user is actively using the machine
            if idle_ms < IDLE_THRESHOLD_MS:
                accumulated_seconds += CHECK_INTERVAL

            # Flush to log file every 5 seconds (protects against sudden shutdown)
            if time.time() - last_log_time >= 5:
                log_today_seconds(accumulated_seconds)
                last_log_time = time.time()

            # Display formatted time on a single line
            formatted = format_hh_mm_ss(accumulated_seconds)
            sys.stdout.write(f"\rScreen On Time (Today): {formatted}  ")
            sys.stdout.flush()

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        log_today_seconds(accumulated_seconds)
        print("\nTracker stopped.")


if __name__ == "__main__":
    main()