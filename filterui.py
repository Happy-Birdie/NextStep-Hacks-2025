# filterui.py
import win32gui
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton
import filterstate

def get_window_titles():
    titles = []
    def enum_callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                results.append(title)
    win32gui.EnumWindows(enum_callback, titles)
    return titles

class FilterUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Window Selection Menu")
        self.setGeometry(100, 100, 320, 180)

        layout = QVBoxLayout()

        self.window_combo = QComboBox()
        self.window_combo.addItems(get_window_titles())
        self.window_combo.currentTextChanged.connect(self.on_window_changed)

        self.refresh_button = QPushButton("Refresh Windows")
        self.refresh_button.clicked.connect(self.refresh_windows)

        layout.addWidget(QLabel("Select Window:"))
        layout.addWidget(self.window_combo)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

        if self.window_combo.count() > 0:
            filterstate.selected_window = self.window_combo.currentText()

    def on_window_changed(self, text):
        filterstate.selected_window = text

    def refresh_windows(self):
        windows = get_window_titles()
        self.window_combo.clear()
        self.window_combo.addItems(windows)

'''
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    # Dummy filterstate fallback for testing
    class DummyFilterState:
        selected_window = None
    filterstate = DummyFilterState()

    app = QApplication(sys.argv)
    window = FilterUI()
    window.show()
    sys.exit(app.exec_())
'''
