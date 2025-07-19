import win32gui, win32ui, win32con
import numpy as np
import cv2
import time
from ctypes import windll

def tritanopia_filter(frame: np.ndarray) -> np.ndarray:
    M = np.array([[0.95, 0.05, 0.0],
                  [0.0, 0.433, 0.567],
                  [0.0, 0.475, 0.525]], dtype=np.float32)
    norm = frame.astype(np.float32) / 255.0
    rgb = norm[..., ::-1]
    sim = np.clip(np.dot(rgb, M.T), 0, 1)
    bgr = (sim[..., ::-1] * 255).astype(np.uint8)
    return bgr

def make_click_through_and_topmost(window_name: str):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        # Set layered and transparent styles
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        styles |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)

        # Optional: set transparency (fully opaque, but still click-through)
        win32gui.SetLayeredWindowAttributes(hwnd, 0x000000, 255, win32con.LWA_ALPHA)

        # Set always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

def capture_with_filter(window_title="Untitled - Notepad"):
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print(f"Window '{window_title}' not found.")
        return

    l, t, r, b = win32gui.GetWindowRect(hwnd)
    w, h = r - l, b - t
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(bmp)

    PW_RENDERFULLCONTENT = 2
    prev = time.time()
    win_name = f"Amblyopia Filter: {window_title}"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(win_name, l, t)
    cv2.resizeWindow(win_name, w, h)

    # Wait briefly to ensure OpenCV creates the window, then set flags
    cv2.waitKey(100)
    make_click_through_and_topmost(win_name)

    while True:
        windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), PW_RENDERFULLCONTENT)

        info = bmp.GetInfo()
        arr = np.frombuffer(bmp.GetBitmapBits(True), dtype=np.uint8)
        arr = arr.reshape((info['bmHeight'], info['bmWidth'], 4))
        frame = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)

        filtered = tritanopia_filter(frame)

        now = time.time()
        fps = int(1.0 / (now - prev)) if now != prev else 0
        prev = now
        cv2.putText(filtered, f"FPS: {fps}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow(win_name, filtered)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.getWindowProperty(win_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.DeleteObject(bmp.GetHandle())
    win32gui.ReleaseDC(hwnd, hwndDC)
    cv2.destroyAllWindows()
    print("Capture stopped and cleaned up.")

'''
if __name__ == "__main__":
    capture_with_filter("Microsoft Store")  # Replace with your target window title
'''
