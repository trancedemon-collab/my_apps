import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QFileDialog, QToolBar
from PyQt6.QtGui import QAction, QIcon

class SimpleNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quick Note")
        self.resize(600, 400)

        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)

        # Toolbar using native system theme icons
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        open_act = QAction(QIcon.fromTheme("document-open"), "Open", self)
        open_act.triggered.connect(self.open_file)
        toolbar.addAction(open_act)

        save_act = QAction(QIcon.fromTheme("document-save"), "Save", self)
        save_act.triggered.connect(self.save_file)
        toolbar.addAction(save_act)

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Note", "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.editor.setPlainText(f.read())

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Note", "", "Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Allows Plasma to associate it with an app identity
    app.setApplicationName("SimpleNotes")
    
    win = SimpleNotes()
    win.show()
    sys.exit(app.exec())