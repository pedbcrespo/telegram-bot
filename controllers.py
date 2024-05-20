import pyautogui as pag

def move(x, y):
    pag.press('space')
    pag.rightClick(x,y)

def action(key):
    pag.press(key)