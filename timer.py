#!/usr/bin/env python3
import sys
import os
import json
import math
import struct
import wave
import subprocess
from PyQt6.QtCore import Qt, QTimer, QCoreApplication
from PyQt6.QtGui import QFont, QColor, QKeySequence, QShortcut, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QSpinBox, QComboBox,
    QDialog, QColorDialog, QFontDialog, QMessageBox, QSlider,
    QFileDialog, QInputDialog, QLineEdit
)
from PyQt6.QtDBus import QDBusInterface, QDBusReply, QDBusMessage

CONFIG_PATH = os.path.expanduser("~/Desktop/timer/timer_config.json")
ICON_PATH = os.path.expanduser("~/Desktop/timer/timer.svg")
TEMP_WAV = "/tmp/timer_alarm.wav"

class SoundSynthesizer:
    current_process = None

    @staticmethod
    def generate_wav(sound_type, freq, pattern, volume, loop_count="3 times", loop_delay=0.5):
        sample_rate = 22050
        duration = 0.4  # duration of a single pulse in seconds
        
        # Determine number of pulses and pause based on pattern
        if pattern == "Single Long":
            pulses = 1
            duration = 0.9
            pause = 0.0
        elif pattern == "Double Beep":
            pulses = 2
            duration = 0.3
            pause = 0.15
        elif pattern == "Triple Pulse":
            pulses = 3
            duration = 0.2
            pause = 0.1
        elif pattern == "Continuous Intermittent":
            pulses = 5
            duration = 0.15
            pause = 0.1
        else: # Default
            pulses = 2
            duration = 0.3
            pause = 0.15

        audio_data = bytearray()
        amp = int(32767 * (volume / 100.0))

        for p in range(pulses):
            num_samples = int(sample_rate * duration)
            for i in range(num_samples):
                t = i / sample_rate
                # Waveform generation
                if sound_type == "Buzzer":
                    # Square wave approximation
                    val = amp if math.sin(2 * math.pi * freq * t) > 0 else -amp
                elif sound_type == "Pulse":
                    # Sawtooth wave
                    val = int(amp * (2 * (t * freq - math.floor(0.5 + t * freq))))
                elif sound_type == "Multi-tone chime":
                    # Chord / harmonics
                    val = int(amp * 0.5 * (math.sin(2 * math.pi * freq * t) + 
                                           math.sin(2 * math.pi * freq * 1.5 * t) + 
                                           math.sin(2 * math.pi * freq * 2.0 * t)) / 1.5)
                else: # Beep (Sine wave)
                    val = int(amp * math.sin(2 * math.pi * freq * t))
                
                audio_data.extend(struct.pack('<h', max(-32768, min(32767, val))))
            
            # Add silence between pulses if multiple
            if p < pulses - 1:
                silence_samples = int(sample_rate * pause)
                audio_data.extend(b'\x00' * (silence_samples * 2))

        # Determine loop/repeat multiplier
        if loop_count == "1 time":
            multiplier = 1
        elif loop_count == "5 times":
            multiplier = 5
        elif loop_count == "10 times":
            multiplier = 10
        elif loop_count == "Loop until dismissed":
            multiplier = 50
        else: # "3 times"
            multiplier = 3

        delay_samples = int(sample_rate * float(loop_delay))
        silence_bytes = b'\x00' * (delay_samples * 2)

        final_audio_data = bytearray()
        for m in range(multiplier):
            final_audio_data.extend(audio_data)
            if m < multiplier - 1 and delay_samples > 0:
                final_audio_data.extend(silence_bytes)

        try:
            with wave.open(TEMP_WAV, 'w') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(final_audio_data)
        except Exception as e:
            print(f"Error generating WAV: {e}")

    @staticmethod
    def play(sound_type, freq, pattern, volume, loop_count="3 times", loop_delay=0.5):
        SoundSynthesizer.stop()
        SoundSynthesizer.generate_wav(sound_type, freq, pattern, volume, loop_count, loop_delay)
        for player in ['paplay', 'pw-cat', 'aplay']:
            try:
                if player == 'paplay':
                    SoundSynthesizer.current_process = subprocess.Popen(['paplay', TEMP_WAV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                elif player == 'pw-cat':
                    SoundSynthesizer.current_process = subprocess.Popen(['pw-cat', '-p', TEMP_WAV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                elif player == 'aplay':
                    SoundSynthesizer.current_process = subprocess.Popen(['aplay', '-q', TEMP_WAV], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

    @staticmethod
    def stop():
        if SoundSynthesizer.current_process:
            try:
                SoundSynthesizer.current_process.terminate()
                SoundSynthesizer.current_process.wait(timeout=0.2)
            except Exception:
                try:
                    SoundSynthesizer.current_process.kill()
                except Exception:
                    pass
            SoundSynthesizer.current_process = None

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Timer Settings")
        self.setFixedSize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Visuals Section
        vis_layout = QGridLayout()
        vis_layout.addWidget(QLabel("<b>Visual Appearance</b>", self), 0, 0, 1, 2)
        
        self.font_btn = QPushButton("Choose Font...", self)
        self.font_btn.clicked.connect(self.choose_font)
        vis_layout.addWidget(self.font_btn, 1, 0)
        
        self.font_label = QLabel(f"{self.config['visuals']['font_family']}, {self.config['visuals']['font_size']}pt", self)
        vis_layout.addWidget(self.font_label, 1, 1)

        self.bg_color_btn = QPushButton("Background Color...", self)
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        vis_layout.addWidget(self.bg_color_btn, 2, 0)
        
        self.bg_color_preview = QLabel(self)
        self.update_color_preview(self.config['visuals']['background_color'])
        vis_layout.addWidget(self.bg_color_preview, 2, 1)

        layout.addLayout(vis_layout)

        # Sound Section
        sound_layout = QGridLayout()
        sound_layout.addWidget(QLabel("<b>Alarm Sound Synthesizer</b>", self), 0, 0, 1, 2)

        sound_layout.addWidget(QLabel("Sound Type:", self), 1, 0)
        self.sound_type_combo = QComboBox(self)
        self.sound_type_combo.addItems(["Beep", "Buzzer", "Pulse", "Multi-tone chime"])
        self.sound_type_combo.setCurrentText(self.config['sound']['type'])
        sound_layout.addWidget(self.sound_type_combo, 1, 1)

        sound_layout.addWidget(QLabel("Frequency (Hz):", self), 2, 0)
        self.freq_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.freq_slider.setRange(200, 2500)
        self.freq_slider.setValue(self.config['sound']['frequency'])
        self.freq_label = QLabel(str(self.config['sound']['frequency']), self)
        self.freq_slider.valueChanged.connect(lambda v: self.freq_label.setText(str(v)))
        
        freq_box = QHBoxLayout()
        freq_box.addWidget(self.freq_slider)
        freq_box.addWidget(self.freq_label)
        sound_layout.addLayout(freq_box, 2, 1)

        sound_layout.addWidget(QLabel("Pattern:", self), 3, 0)
        self.pattern_combo = QComboBox(self)
        self.pattern_combo.addItems(["Single Long", "Double Beep", "Triple Pulse", "Continuous Intermittent"])
        self.pattern_combo.setCurrentText(self.config['sound']['pattern'])
        sound_layout.addWidget(self.pattern_combo, 3, 1)

        sound_layout.addWidget(QLabel("Volume (%):", self), 4, 0)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.vol_slider.setRange(10, 100)
        self.vol_slider.setValue(self.config['sound']['volume'])
        self.vol_label = QLabel(str(self.config['sound']['volume']), self)
        self.vol_slider.valueChanged.connect(lambda v: self.vol_label.setText(str(v)))
        
        vol_box = QHBoxLayout()
        vol_box.addWidget(self.vol_slider)
        vol_box.addWidget(self.vol_label)
        sound_layout.addLayout(vol_box, 4, 1)

        sound_layout.addWidget(QLabel("Beep Loop:", self), 5, 0)
        self.loop_combo = QComboBox(self)
        self.loop_combo.addItems(["1 time", "3 times", "5 times", "10 times", "Loop until dismissed"])
        self.loop_combo.setCurrentText(self.config['sound'].get('loop_count', '3 times'))
        sound_layout.addWidget(self.loop_combo, 5, 1)

        sound_layout.addWidget(QLabel("Loop Delay (s):", self), 6, 0)
        self.delay_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.delay_slider.setRange(0, 30) # 0.0s to 3.0s
        default_delay = self.config['sound'].get('loop_delay', 0.5)
        self.delay_slider.setValue(int(default_delay * 10))
        self.delay_label = QLabel(f"{default_delay:.1f}s", self)
        self.delay_slider.valueChanged.connect(lambda v: self.delay_label.setText(f"{v/10.0:.1f}s"))
        
        delay_box = QHBoxLayout()
        delay_box.addWidget(self.delay_slider)
        delay_box.addWidget(self.delay_label)
        sound_layout.addLayout(delay_box, 6, 1)

        self.test_btn = QPushButton("Test Sound", self)
        self.test_btn.clicked.connect(self.test_sound)
        sound_layout.addWidget(self.test_btn, 7, 0, 1, 2)

        layout.addLayout(sound_layout)

        # Dialog Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def choose_font(self):
        current_font = QFont(self.config['visuals']['font_family'], self.config['visuals']['font_size'])
        font, ok = QFontDialog.getFont(current_font, self, "Select Timer Font")
        if ok:
            self.config['visuals']['font_family'] = font.family()
            self.config['visuals']['font_size'] = font.pointSize()
            self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")

    def choose_bg_color(self):
        color = QColorDialog.getColor(QColor(self.config['visuals']['background_color']), self, "Select Background Color")
        if color.isValid():
            hex_str = color.name()
            self.config['visuals']['background_color'] = hex_str
            self.update_color_preview(hex_str)

    def update_color_preview(self, hex_col):
        self.bg_color_preview.setStyleSheet(f"background-color: {hex_col}; border: 1px solid gray;")
        self.bg_color_preview.setFixedSize(60, 25)

    def test_sound(self):
        if SoundSynthesizer.current_process and SoundSynthesizer.current_process.poll() is None:
            SoundSynthesizer.stop()
            self.test_btn.setText("Test Sound")
        else:
            st = self.sound_type_combo.currentText()
            freq = self.freq_slider.value()
            pat = self.pattern_combo.currentText()
            vol = self.vol_slider.value()
            loop_c = self.loop_combo.currentText()
            loop_d = self.delay_slider.value() / 10.0
            SoundSynthesizer.play(st, freq, pat, vol, loop_c, loop_d)
            self.test_btn.setText("Stop Test Sound")

    def save_settings(self):
        self.config['sound']['type'] = self.sound_type_combo.currentText()
        self.config['sound']['frequency'] = self.freq_slider.value()
        self.config['sound']['pattern'] = self.pattern_combo.currentText()
        self.config['sound']['volume'] = self.vol_slider.value()
        self.config['sound']['loop_count'] = self.loop_combo.currentText()
        self.config['sound']['loop_delay'] = self.delay_slider.value() / 10.0
        SoundSynthesizer.stop()
        self.accept()

    def closeEvent(self, event):
        SoundSynthesizer.stop()
        event.accept()


class TimerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.remaining_seconds = 0
        self.total_seconds = 0
        self.is_running = False
        self.inhibit_cookie = None

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_tick)

        self.init_ui()
        self.setup_shortcuts()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r') as f:
                    self.config = json.load(f)
            except Exception:
                self.config = self.default_config()
        else:
            self.config = self.default_config()
            self.save_config()

    def default_config(self):
        return {
            "presets": [
                {"name": "Pomodoro (25m)", "hours": 0, "minutes": 25, "seconds": 0},
                {"name": "Short Break (5m)", "hours": 0, "minutes": 5, "seconds": 0},
                {"name": "Long Break (15m)", "hours": 0, "minutes": 15, "seconds": 0}
            ],
            "visuals": {
                "font_family": "Sans Serif",
                "font_size": 44,
                "background_color": "#1e1e1e",
                "text_color": "#3daee9"
            },
            "sound": {
                "type": "Multi-tone chime",
                "frequency": 880,
                "pattern": "Triple Pulse",
                "volume": 80
            },
            "last_timer": {
                "hours": 0,
                "minutes": 25,
                "seconds": 0
            }
        }

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def init_ui(self):
        self.setWindowTitle("KDE Desktop Timer")
        self.setFixedSize(500, 310)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Top Bar: Presets & Settings Button
        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("Preset:", self))
        
        self.preset_combo = QComboBox(self)
        self.update_preset_combo()
        self.preset_combo.currentIndexChanged.connect(self.on_preset_selected)
        top_bar.addWidget(self.preset_combo, 1)

        self.save_preset_btn = QPushButton("Save Preset", self)
        self.save_preset_btn.clicked.connect(self.save_current_as_preset)
        top_bar.addWidget(self.save_preset_btn)

        self.del_preset_btn = QPushButton("Delete", self)
        self.del_preset_btn.clicked.connect(self.delete_preset)
        top_bar.addWidget(self.del_preset_btn)

        self.settings_btn = QPushButton("⚙ Settings", self)
        self.settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(self.settings_btn)

        main_layout.addLayout(top_bar)

        # Clock Display Panel
        self.display_label = QLabel("00:00:00", self)
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_display_style()
        main_layout.addWidget(self.display_label)

        # Inputs Panel (Hours, Minutes, Seconds Spinboxes)
        input_layout = QHBoxLayout()
        input_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        last = self.config.get('last_timer', {"hours": 0, "minutes": 25, "seconds": 0})

        self.hour_spin = QSpinBox(self)
        self.hour_spin.setRange(0, 23)
        self.hour_spin.setPrefix("H: ")
        self.hour_spin.setFixedWidth(100)
        self.hour_spin.setFont(QFont("Sans Serif", 11))
        self.hour_spin.setValue(last.get('hours', 0))
        self.hour_spin.valueChanged.connect(self.on_spin_changed)

        self.min_spin = QSpinBox(self)
        self.min_spin.setRange(0, 59)
        self.min_spin.setPrefix("M: ")
        self.min_spin.setFixedWidth(100)
        self.min_spin.setFont(QFont("Sans Serif", 11))
        self.min_spin.setValue(last.get('minutes', 25))
        self.min_spin.valueChanged.connect(self.on_spin_changed)

        self.sec_spin = QSpinBox(self)
        self.sec_spin.setRange(0, 59)
        self.sec_spin.setPrefix("S: ")
        self.sec_spin.setFixedWidth(100)
        self.sec_spin.setFont(QFont("Sans Serif", 11))
        self.sec_spin.setValue(last.get('seconds', 0))
        self.sec_spin.valueChanged.connect(self.on_spin_changed)

        input_layout.addWidget(self.hour_spin)
        input_layout.addWidget(self.min_spin)
        input_layout.addWidget(self.sec_spin)
        main_layout.addLayout(input_layout)

        # Control Buttons (Start/Pause, Stop)
        ctrl_layout = QHBoxLayout()
        
        self.start_pause_btn = QPushButton("Start (Space)", self)
        self.start_pause_btn.setFixedHeight(40)
        self.start_pause_btn.setStyleSheet("font-weight: bold; font-size: 14pt; background-color: #1d99f3; color: white;")
        self.start_pause_btn.clicked.connect(self.toggle_start_pause)
        ctrl_layout.addWidget(self.start_pause_btn, 2)

        self.stop_btn = QPushButton("Stop (Esc)", self)
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setStyleSheet("font-size: 14pt;")
        self.stop_btn.clicked.connect(self.stop_timer)
        ctrl_layout.addWidget(self.stop_btn, 1)

        main_layout.addLayout(ctrl_layout)

        # Initialize remaining seconds from spinboxes
        self.update_remaining_from_spins()

    def update_preset_combo(self):
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("-- Custom --", None)
        for p in self.config['presets']:
            self.preset_combo.addItem(p['name'], p)
        self.preset_combo.blockSignals(False)

    def update_display_style(self):
        vis = self.config['visuals']
        font = QFont(vis['font_family'], vis['font_size'], QFont.Weight.Bold)
        self.display_label.setFont(font)
        self.display_label.setStyleSheet(
            f"background-color: {vis['background_color']}; "
            f"color: {vis['text_color']}; "
            f"border-radius: 8px; padding: 10px;"
        )

    def setup_shortcuts(self):
        self.space_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        self.space_shortcut.activated.connect(self.toggle_start_pause)

        self.esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.esc_shortcut.activated.connect(self.stop_timer)

    def save_last_timer(self):
        self.config['last_timer'] = {
            "hours": self.hour_spin.value(),
            "minutes": self.min_spin.value(),
            "seconds": self.sec_spin.value()
        }
        self.save_config()

    def on_spin_changed(self):
        if not self.is_running:
            self.update_remaining_from_spins()
            self.save_last_timer()
            self.preset_combo.blockSignals(True)
            self.preset_combo.setCurrentIndex(0)
            self.preset_combo.blockSignals(False)

    def update_remaining_from_spins(self):
        h = self.hour_spin.value()
        m = self.min_spin.value()
        s = self.sec_spin.value()
        self.total_seconds = h * 3600 + m * 60 + s
        self.remaining_seconds = self.total_seconds
        self.update_display()

    def update_display(self):
        h = self.remaining_seconds // 3600
        m = (self.remaining_seconds % 3600) // 60
        s = self.remaining_seconds % 60
        self.display_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def toggle_start_pause(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.remaining_seconds <= 0:
            self.update_remaining_from_spins()
        if self.remaining_seconds <= 0:
            return  # Nothing to run

        self.is_running = True
        self.start_pause_btn.setText("Pause (Space)")
        self.start_pause_btn.setStyleSheet("font-weight: bold; font-size: 14pt; background-color: #f67400; color: white;")
        
        # Disable spinboxes and presets while running
        self.hour_spin.setEnabled(False)
        self.min_spin.setEnabled(False)
        self.sec_spin.setEnabled(False)
        self.preset_combo.setEnabled(False)
        self.save_preset_btn.setEnabled(False)
        self.del_preset_btn.setEnabled(False)

        self.timer.start()
        self.inhibit_sleep()

    def pause_timer(self):
        self.is_running = False
        self.timer.stop()
        self.start_pause_btn.setText("Resume (Space)")
        self.start_pause_btn.setStyleSheet("font-weight: bold; font-size: 14pt; background-color: #1d99f3; color: white;")
        self.uninhibit_sleep()

    def stop_timer(self):
        self.is_running = False
        self.timer.stop()
        self.uninhibit_sleep()
        self.start_pause_btn.setText("Start (Space)")
        self.start_pause_btn.setStyleSheet("font-weight: bold; font-size: 14pt; background-color: #1d99f3; color: white;")
        
        # Re-enable inputs
        self.hour_spin.setEnabled(True)
        self.min_spin.setEnabled(True)
        self.sec_spin.setEnabled(True)
        self.preset_combo.setEnabled(True)
        self.save_preset_btn.setEnabled(True)
        self.del_preset_btn.setEnabled(True)

        self.update_remaining_from_spins()

    def on_tick(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
        
        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.is_running = False
            self.uninhibit_sleep()
            
            # Play alarm sound asynchronously
            sound = self.config['sound']
            SoundSynthesizer.play(sound['type'], sound['frequency'], sound['pattern'], sound['volume'], sound.get('loop_count', '3 times'), sound.get('loop_delay', 0.5))

            QMessageBox.information(self, "Timer Finished", "Time is up!")
            
            # Stop audio immediately upon dismissing the message box
            SoundSynthesizer.stop()
            self.stop_timer()

    def on_preset_selected(self, index):
        if index > 0:
            data = self.preset_combo.currentData()
            if data:
                self.hour_spin.setValue(data['hours'])
                self.min_spin.setValue(data['minutes'])
                self.sec_spin.setValue(data['seconds'])
                self.save_last_timer()

    def save_current_as_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset Name:")
        if ok and name.strip():
            new_preset = {
                "name": name.strip(),
                "hours": self.hour_spin.value(),
                "minutes": self.min_spin.value(),
                "seconds": self.sec_spin.value()
            }
            self.config['presets'].append(new_preset)
            self.save_config()
            self.update_preset_combo()
            self.preset_combo.setCurrentText(name.strip())

    def delete_preset(self):
        idx = self.preset_combo.currentIndex()
        if idx > 0:
            preset_data = self.preset_combo.currentData()
            self.config['presets'] = [p for p in self.config['presets'] if p['name'] != preset_data['name']]
            self.save_config()
            self.update_preset_combo()

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.save_config()
            self.update_display_style()

    def inhibit_sleep(self):
        if self.inhibit_cookie is not None:
            return
        try:
            # Try FreeDesktop ScreenSaver Inhibit
            bus = QDBusInterface("org.freedesktop.ScreenSaver", "/ScreenSaver", "org.freedesktop.ScreenSaver")
            if bus.isValid():
                reply = bus.call("Inhibit", "KDE Desktop Timer", "Timer is actively running")
                if reply.type() == QDBusMessage.MessageType.ReplyMessage and reply.arguments():
                    cookie = reply.arguments()[0]
                    if hasattr(cookie, "variant"):
                        cookie = cookie.variant()
                    self.inhibit_cookie = int(cookie)
                    return
            
            # Fallback to PowerManagement Inhibit
            bus_pm = QDBusInterface("org.freedesktop.PowerManagement.Inhibit", "/org/freedesktop/PowerManagement/Inhibit", "org.freedesktop.PowerManagement.Inhibit")
            if bus_pm.isValid():
                reply = bus_pm.call("Inhibit", "KDE Desktop Timer", "Timer is actively running")
                if reply.type() == QDBusMessage.MessageType.ReplyMessage and reply.arguments():
                    cookie = reply.arguments()[0]
                    if hasattr(cookie, "variant"):
                        cookie = cookie.variant()
                    self.inhibit_cookie = int(cookie)
        except Exception as e:
            print(f"Could not inhibit sleep: {e}")

    def uninhibit_sleep(self):
        if self.inhibit_cookie is None:
            return
        cookie = self.inhibit_cookie
        self.inhibit_cookie = None
        try:
            bus = QDBusInterface("org.freedesktop.ScreenSaver", "/ScreenSaver", "org.freedesktop.ScreenSaver")
            if bus.isValid():
                bus.call("UnInhibit", cookie)
            else:
                bus_pm = QDBusInterface("org.freedesktop.PowerManagement.Inhibit", "/org/freedesktop/PowerManagement/Inhibit", "org.freedesktop.PowerManagement.Inhibit")
                if bus_pm.isValid():
                    bus_pm.call("UnInhibit", cookie)
        except Exception as e:
            print(f"Could not uninhibit sleep: {e}")

    def closeEvent(self, event):
        self.uninhibit_sleep()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TimerWindow()
    window.show()
    sys.exit(app.exec())
