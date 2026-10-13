import sys
import os
import json
import time
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QWidget, QVBoxLayout, 
    QHBoxLayout, QSplitter, QListWidget, QLineEdit, QPushButton, 
    QComboBox, QLabel, QMessageBox, QFrame, QSpinBox, QCheckBox, QDialog, QFormLayout, QListWidgetItem, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QFontDatabase

NOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_notes.json")

class PlainTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptRichText(False)
        font = QFont("Monospace")
        font.setStyleHint(QFont.StyleHint.Monospace)
        font.setPointSize(11)
        self.setFont(font)

    def insertFromMimeData(self, source):
        if source.hasText():
            text = source.text()
            lines = text.splitlines(keepends=True)
            cleaned_lines = []
            for line in lines:
                line = line.replace('\t', '    ')
                line = line.replace('\ufffc', '')
                stripped = line.lstrip()
                if stripped.startswith(('•', '◦', '▪', '▫', '‣', '⁃', '∙')):
                    bullet_char = stripped[0]
                    idx = line.find(bullet_char)
                    if idx != -1:
                        line = line[:idx] + line[idx + len(bullet_char):].lstrip(' \t')
                cleaned_lines.append(line)
            text = "".join(cleaned_lines)
            self.insertPlainText(text)
        else:
            super().insertFromMimeData(source)

class SettingsDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("Settings & Purge Options")
        self.resize(380, 300)
        self.settings = settings

        layout = QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.purge_enabled_cb = QCheckBox("Enable Auto-Purge")
        self.purge_enabled_cb.setChecked(settings.get("auto_purge_enabled", False))
        layout.addRow(self.purge_enabled_cb)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10000)
        self.interval_spin.setValue(settings.get("purge_interval_value", 30))
        layout.addRow("Purge interval:", self.interval_spin)

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Hours", "Days", "Months", "Years"])
        current_unit = settings.get("purge_interval_unit", "Days")
        idx = self.unit_combo.findText(current_unit)
        if idx >= 0:
            self.unit_combo.setCurrentIndex(idx)
        layout.addRow("Interval unit:", self.unit_combo)

        self.max_notes_spin = QSpinBox()
        self.max_notes_spin.setRange(5, 1000)
        self.max_notes_spin.setValue(settings.get("max_notes_display", 100))
        layout.addRow("Max notes displayed:", self.max_notes_spin)

        nuke_btn = QPushButton("💥 Nuke All Data")
        nuke_btn.setStyleSheet("color: red; font-weight: bold;")
        nuke_btn.clicked.connect(self.parent().nuke_all_data)
        layout.addRow(nuke_btn)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

    def get_settings(self):
        return {
            "auto_purge_enabled": self.purge_enabled_cb.isChecked(),
            "purge_interval_value": self.interval_spin.value(),
            "purge_interval_unit": self.unit_combo.currentText(),
            "max_notes_display": self.max_notes_spin.value()
        }


class SimpleNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quick Notes")
        self.resize(1100, 700)

        self.notes_data = self.load_data()
        self.run_auto_purge()

        self.active_note_id = self.notes_data.get("active_note", "")
        notes = self.notes_data.get("notes", {})
        
        if self.active_note_id not in notes and notes:
            self.active_note_id = list(notes.keys())[0]
            self.notes_data["active_note"] = self.active_note_id
        elif not notes:
            self.active_note_id = None
            self.notes_data["active_note"] = None

        self.note_ids_order = []
        self.init_ui()
        self.init_shortcuts()
        if self.active_note_id and self.active_note_id in notes:
            self.load_note_into_ui(self.active_note_id)
        else:
            self.clear_ui()

    def load_data(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "notes" in data:
                        if "settings" not in data:
                            data["settings"] = {
                                "auto_purge_enabled": False,
                                "purge_interval_value": 30,
                                "purge_interval_unit": "Days",
                                "max_notes_display": 100
                            }
                        return data
            except Exception:
                pass
        
        now = time.time()
        return {
            "active_note": "note_1",
            "settings": {
                "auto_purge_enabled": False,
                "purge_interval_value": 30,
                "purge_interval_unit": "Days",
                "max_notes_display": 100
            },
            "notes": {
                "note_1": {
                    "title": "untitled001",
                    "content": "Welcome to Quick Notes!",
                    "created_at": now,
                    "updated_at": now,
                    "starred": False
                }
            }
        }

    def save_data(self):
        self.sync_active_note_from_ui()
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.notes_data, f, indent=4)
        except Exception as e:
            print("Error saving notes:", e)

    def save_data_silent(self):
        self.sync_active_note_from_ui()
        try:
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.notes_data, f, indent=4)
        except Exception:
            pass

    def sync_active_note_from_ui(self):
        if not self.active_note_id:
            return
        notes = self.notes_data.setdefault("notes", {})
        if self.active_note_id in notes:
            note = notes[self.active_note_id]
            note["title"] = self.title_input.text()
            note["content"] = self.editor.toPlainText()
            note["updated_at"] = time.time()
        self.notes_data["active_note"] = self.active_note_id

    def get_next_untitled_title(self):
        notes = self.notes_data.get("notes", {})
        max_num = 0
        for n_data in notes.values():
            title = n_data.get("title", "")
            match = re.match(r"^untitled(\d+)$", title, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        return f"untitled{max_num + 1:03d}"

    def run_auto_purge(self):
        settings = self.notes_data.get("settings", {})
        if not settings.get("auto_purge_enabled", False):
            return
        
        val = settings.get("purge_interval_value", 30)
        unit = settings.get("purge_interval_unit", "Days")
        
        multiplier = 86400
        if unit == "Hours":
            multiplier = 3600
        elif unit == "Days":
            multiplier = 86400
        elif unit == "Months":
            multiplier = 86400 * 30
        elif unit == "Years":
            multiplier = 86400 * 365
            
        threshold_seconds = val * multiplier
        now = time.time()
        
        notes = self.notes_data.get("notes", {})
        to_delete = []
        for n_id, n_data in notes.items():
            if n_data.get("starred", False):
                continue
            timestamp = n_data.get("updated_at", n_data.get("created_at", now))
            if now - timestamp > threshold_seconds:
                to_delete.append(n_id)
                
        for n_id in to_delete:
            del notes[n_id]

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Header Bar: Title & Options
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        top_bar.addWidget(QLabel("<b>Note Title:</b>"))
        
        self.title_input = QLineEdit()
        self.title_input.textChanged.connect(self.on_title_changed)
        top_bar.addWidget(self.title_input, stretch=1)

        new_note_btn = QPushButton("New Note")
        new_note_btn.clicked.connect(self.create_new_note)
        top_bar.addWidget(new_note_btn)

        self.star_btn = QPushButton("⭐ Star (Ctrl+S)")
        self.star_btn.setToolTip("Toggle star on current note for auto-purge immunity (Ctrl+S)")
        self.star_btn.clicked.connect(self.toggle_current_star)
        top_bar.addWidget(self.star_btn)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setToolTip("Copy note contents to clipboard")
        copy_btn.clicked.connect(self.copy_note_to_clipboard)
        top_bar.addWidget(copy_btn)

        save_as_btn = QPushButton("💾 Save As...")
        save_as_btn.setToolTip("Save current note as text file anywhere on system")
        save_as_btn.clicked.connect(self.save_note_as_txt)
        top_bar.addWidget(save_as_btn)

        del_note_btn = QPushButton("Delete Note (Ctrl+Del)")
        del_note_btn.setToolTip("Delete current note (Ctrl+Del)")
        del_note_btn.clicked.connect(self.delete_current_note)
        top_bar.addWidget(del_note_btn)

        settings_btn = QPushButton("⚙ Settings")
        settings_btn.clicked.connect(self.open_settings)
        top_bar.addWidget(settings_btn)

        main_layout.addLayout(top_bar)

        # Main Splitter (Left: Notes List, Right: Note Editor)
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(10)
        main_layout.addWidget(main_splitter, stretch=1)

        # Left Panel: Notes list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 12, 0)
        left_layout.setSpacing(10)
        left_layout.addWidget(QLabel("<b>All Notes (★ = Starred)</b>"))
        
        self.notes_list_widget = QListWidget()
        self.notes_list_widget.currentRowChanged.connect(self.on_note_selection_changed)
        left_layout.addWidget(self.notes_list_widget)
        
        main_splitter.addWidget(left_widget)

        # Right Panel: Note Editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(12, 0, 0, 0)
        right_layout.setSpacing(10)
        
        right_layout.addWidget(QLabel("<b>Note Content</b>"))
        
        self.editor = PlainTextEdit()
        self.editor.textChanged.connect(self.on_content_changed)
        right_layout.addWidget(self.editor, stretch=1)

        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([260, 740])

        self.refresh_notes_list()

    def init_shortcuts(self):
        self.shortcut_del = QShortcut(QKeySequence("Ctrl+Del"), self)
        self.shortcut_del.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_del.activated.connect(self.delete_current_note)

        self.shortcut_star = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_star.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_star.activated.connect(self.toggle_current_star)

        self.shortcut_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        self.shortcut_esc.setContext(Qt.ShortcutContext.ApplicationShortcut)
        self.shortcut_esc.activated.connect(self.confirm_and_quit)

    def copy_note_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.editor.toPlainText())
        self.statusBar().showMessage("Note contents copied to clipboard!", 2500)

    def save_note_as_txt(self):
        if not self.active_note_id:
            QMessageBox.warning(self, "Warning", "No active note to save.")
            return
        self.sync_active_note_from_ui()
        notes = self.notes_data.get("notes", {})
        if self.active_note_id in notes:
            note = notes[self.active_note_id]
            default_title = note.get("title", "note") + ".txt"
            path, _ = QFileDialog.getSaveFileName(self, "Save Note As Text File", default_title, "Text Files (*.txt);;All Files (*)")
            if path:
                try:
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(note.get("content", ""))
                    self.statusBar().showMessage(f"Saved note to {path}", 3500)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def confirm_and_quit(self):
        reply = QMessageBox.question(self, "Quit", "Are you sure you want to quit Quick Notes?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.close()

    def nuke_all_data(self):
        reply = QMessageBox.critical(
            self, 
            "⚠️ NUKE ALL DATA WARNING", 
            "Are you absolutely sure you want to delete ALL notes and settings? This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            now = time.time()
            self.notes_data = {
                "active_note": None,
                "settings": {
                    "auto_purge_enabled": False,
                    "purge_interval_value": 30,
                    "purge_interval_unit": "Days",
                    "max_notes_display": 100
                },
                "notes": {}
            }
            self.active_note_id = None
            self.save_data()
            self.refresh_notes_list(preserve_selection=False)
            self.clear_ui()
            self.statusBar().showMessage("All data has been nuked and reset.", 4000)

    def clear_ui(self):
        self.title_input.blockSignals(True)
        self.title_input.clear()
        self.title_input.setEnabled(False)
        self.title_input.blockSignals(False)

        self.editor.blockSignals(True)
        self.editor.clear()
        self.editor.setEnabled(False)
        self.editor.blockSignals(False)

    def refresh_notes_list(self, preserve_selection=False):
        current_row = self.notes_list_widget.currentRow()
        self.notes_list_widget.blockSignals(True)
        self.notes_list_widget.clear()
        
        self.note_ids_order = []
        notes = self.notes_data.get("notes", {})
        max_display = self.notes_data.get("settings", {}).get("max_notes_display", 100)
        
        sorted_notes = sorted(notes.items(), key=lambda x: x[1].get("updated_at", 0), reverse=True)
        if len(sorted_notes) > max_display:
            sorted_notes = sorted_notes[:max_display]

        for note_id, note_data in sorted_notes:
            self.note_ids_order.append(note_id)
            title = note_data.get("title", "Untitled")
            starred = note_data.get("starred", False)
            prefix = "★ " if starred else "   "
            item = QListWidgetItem(f"{prefix}{title}")
            self.notes_list_widget.addItem(item)
            
        if notes:
            if preserve_selection and 0 <= current_row < len(self.note_ids_order):
                self.notes_list_widget.setCurrentRow(current_row)
            elif self.active_note_id in self.note_ids_order:
                idx = self.note_ids_order.index(self.active_note_id)
                self.notes_list_widget.setCurrentRow(idx)
            elif self.note_ids_order:
                self.notes_list_widget.setCurrentRow(0)
        else:
            self.clear_ui()
            
        self.notes_list_widget.blockSignals(False)

    def load_note_into_ui(self, note_id):
        notes = self.notes_data.get("notes", {})
        if note_id not in notes:
            self.clear_ui()
            return
        
        self.active_note_id = note_id
        note = notes[note_id]
        
        self.title_input.setEnabled(True)
        self.title_input.blockSignals(True)
        self.title_input.setText(note.get("title", ""))
        self.title_input.blockSignals(False)

        self.editor.setEnabled(True)
        self.editor.blockSignals(True)
        self.editor.setPlainText(note.get("content", ""))
        self.editor.blockSignals(False)

    def on_note_selection_changed(self, row):
        if 0 <= row < len(self.note_ids_order):
            self.sync_active_note_from_ui()
            new_id = self.note_ids_order[row]
            if new_id != self.active_note_id:
                self.active_note_id = new_id
                self.load_note_into_ui(new_id)
                self.notes_data["active_note"] = new_id
                self.save_data()

    def toggle_current_star(self):
        notes = self.notes_data.get("notes", {})
        if self.active_note_id and self.active_note_id in notes:
            current = notes[self.active_note_id].get("starred", False)
            notes[self.active_note_id]["starred"] = not current
            self.refresh_notes_list(preserve_selection=True)
            self.save_data()

    def open_settings(self):
        settings = self.notes_data.setdefault("settings", {})
        dlg = SettingsDialog(self, settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.notes_data["settings"] = dlg.get_settings()
            self.save_data()
            self.refresh_notes_list(preserve_selection=True)

    def on_title_changed(self, text):
        if self.active_note_id and self.active_note_id in self.notes_data.get("notes", {}):
            self.notes_data["notes"][self.active_note_id]["title"] = text
            self.notes_data["notes"][self.active_note_id]["updated_at"] = time.time()
        self.refresh_notes_list(preserve_selection=True)
        self.save_data_silent()

    def on_content_changed(self):
        if self.active_note_id:
            self.save_data_silent()

    def create_new_note(self):
        self.sync_active_note_from_ui()
        new_id = f"note_{int(time.time()*1000)}"
        title = self.get_next_untitled_title()
        now = time.time()
        self.notes_data.setdefault("notes", {})[new_id] = {
            "title": title,
            "content": "",
            "created_at": now,
            "updated_at": now,
            "starred": False
        }
        self.active_note_id = new_id
        self.notes_data["active_note"] = new_id
        self.refresh_notes_list(preserve_selection=False)
        self.load_note_into_ui(new_id)
        self.save_data()

    def delete_current_note(self):
        notes = self.notes_data.get("notes", {})
        if not self.active_note_id or self.active_note_id not in notes:
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this note?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del notes[self.active_note_id]
            if notes:
                self.active_note_id = list(notes.keys())[0]
                self.notes_data["active_note"] = self.active_note_id
                self.refresh_notes_list(preserve_selection=False)
                self.load_note_into_ui(self.active_note_id)
            else:
                self.active_note_id = None
                self.notes_data["active_note"] = None
                self.refresh_notes_list(preserve_selection=False)
                self.clear_ui()
            self.save_data()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("SimpleNotes")
    
    win = SimpleNotes()
    win.show()
    sys.exit(app.exec())
