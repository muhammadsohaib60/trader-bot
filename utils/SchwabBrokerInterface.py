import pyautogui


def Buy():
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.click(660, 350)       # click
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.hotkey('alt', 'b')


def Sell():
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.click(660, 350)  # click
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.hotkey('alt', 's')


def Short():
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.click(660, 350)  # click
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.hotkey('alt', 's')

def CancelAll():
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.click(660, 350)  # click
    pyautogui.moveTo(660, 350, duration=0.1)  # move over window top tab area
    pyautogui.hotkey('alt', 'c')
