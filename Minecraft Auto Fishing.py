import win32gui
import win32ui
import win32con
from PIL import Image
from cnocr import CnOcr
import time


# 获取后台窗口的句柄，注意后台窗口不能最小化
def find_window_by_title(title_substring):
    def enum_window_callback(hwnd, array):
        if title_substring.lower() in win32gui.GetWindowText(hwnd).lower():
            array.append(hwnd)
    windows = []
    win32gui.EnumWindows(enum_window_callback, windows)
    return windows[0] if windows else None


# 截图
def capture_window(hwnd, rect):
    if not hwnd: return

    # 计算右下方 1/5 区域
    left, top, right, bottom = rect
    width, height = right - left, bottom - top

    # 右下方 1/5 的区域
    capture_rect = (right - width // 4, bottom - height // 2, right, bottom)

    # 获取窗口大小
    width, height = capture_rect[2] - capture_rect[0], capture_rect[3] - capture_rect[1]

    # 获取窗口的设备环境并创建内存设备描述表
    hWndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hWndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # 创建位图对象
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # 截图并保存到内存
    # saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (capture_rect[0] - left, capture_rect[1] - top), win32con.SRCCOPY)

    # 将截图保存为PIL图像
    img = Image.frombuffer('RGBA', (width, height), saveBitMap.GetBitmapBits(True), 'raw', 'BGRA', width * 4, 1)

    # 清理资源
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hWndDC)

    return img


# OCR识别文字，检测是否上鱼
def text_detect(img):
    ocr = CnOcr()
    res = ocr.ocr(img)
    for line in res:
        if '浮漂' in line['text'] and '溅起水花' in line['text']:
            return True
    return False


# 收杆
def right_click(hwndr, rectr):
    def makelong(low, high):
        return (int(high) << 16) | (int(low) & 0xFFFF)
    x, y = (rectr[0] + rectr[2]) / 2, (rectr[1] + rectr[3]) / 2
    win32gui.SendMessage(hwndr, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, makelong(x, y)) # 鼠标按下
    win32gui.SendMessage(hwndr, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, makelong(x, y)) # 鼠标弹起

if __name__ =='__main__':
    print("开启自动钓鱼，请回到游戏内抛出鱼竿，按F3+P即可不暂停游戏转入后台")
    hwnd = find_window_by_title('minecraft*')
    count = 0
    while 1:
        rect = win32gui.GetWindowRect(hwnd) # 获取窗口坐标 left, top, right, bottom
        img = capture_window(hwnd, rect)
        if text_detect(img):
            right_click(hwnd, rect)
            print("[次数:]", count ,"收杆")
            time.sleep(3)
            right_click(hwnd, rect)
            print("[次数:]", count ,"抛竿")
            count += 1

