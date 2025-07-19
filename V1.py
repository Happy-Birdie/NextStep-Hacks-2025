import sys
import numpy as np
import pyautogui
import cv2
import time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QDesktopWidget

# Capture the screen
def capture_screen():
    screen = QApplication.primaryScreen()
    screenshot = screen.grabWindow(0)
    ## Read the image
    #screenshot = cv2.imread("img.avif")
    # Convert the QPixmap to QImage
    screenshot = screenshot.toImage().convertToFormat(QImage.Format_RGB888)
    width = screenshot.width()
    height = screenshot.height()
    ptr = screenshot.bits()
    ptr.setsize(height * width * 3)
    # Convert the QImage to a NumPy array
    screen_np = np.array(ptr).reshape(height, width, 3)
    # Convert RGB to BGR (OpenCV format)
    screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
    return screen_bgr

# Apply color filter (example: blue filter)
def apply_color_filter(image):
    # Increase blue channel while decreasing others (example: blue filter)
    image[:, :, 0] = np.clip(image[:, :, 0] - 50, 0, 255)  # Blue channel
    #image[:, :, 1] = np.clip(image[:, :, 1] - 20, 0, 255)  # Green channel
    image[:, :, 2] = np.clip(image[:, :, 2] + 50, 0, 255)  # Red channel
    return image

# Convert the image to a format suitable for PyQt
def convert_to_qimage(image):
    # Convert the image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, channels = image_rgb.shape
    bytes_per_line = 3 * width
    return QImage(image_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        # Make the window transparent, borderless, and non-interactive
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.5)  # Adjust the opacity of the window as needed
        
        # Set the window to full screen
        self.showFullScreen()

        # Timer to update the overlay every 10 milliseconds (to maintain real-time capture)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_overlay)
        self.timer.start(10)

    def initUI(self):
        # Create a QLabel to display the image
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(True)
        self.label.setGeometry(self.rect())
        
        # Capture the screen and apply the color filter once
        self.filtered_screen = apply_color_filter(capture_screen())

    def resizeEvent(self, event):
        self.label.setGeometry(self.rect())
        super().resizeEvent(event)

    def update_overlay(self):
        # Convert to QImage for display in PyQt
        qimage = convert_to_qimage(self.filtered_screen)

        # Display the filtered image in the overlay
        self.label.setPixmap(QPixmap.fromImage(qimage))

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and display the overlay window
    
    while True:
        window = OverlayWindow()
        window.show()
        #time.sleep(1)
        #window2 = OverlayWindow()
        #window2.show()

        sys.exit(app.exec_())
