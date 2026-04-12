import win32gui
import time
import pydirectinput
import vgamepad as vg

PREV_ACTION = []
controller : vg.VDS4Gamepad

def find_activate_window() -> None:
    """
    Function used to activate the Elden Ring game window

    Args:
        None

    Returns:
        None
    """
    hwnd = win32gui.FindWindow(None, "ELDEN RING™")
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
        win32gui.SetActiveWindow(hwnd)
        # WAKE UP PLEAAAAAAAAAAAASEEEEEEEEE
        key_presses(['['] * 12)
        time.sleep(.1)
        key_presses(['['] * 12)
    else:
        "Window Not Found"

def client_window_size() -> list:
    hwnd = win32gui.FindWindow(None, "ELDEN RING™")
    win32gui.MoveWindow(hwnd, 0, 0, 800 + 24, 450 + 64, True)
    return win32gui.GetClientRect(hwnd)

def key_presses(keys: list) -> None:
    """
    Function used to 'press' down multiple keys in succession

    Args:
        key: the list of keys to press

    Returns:
        None
    """
    for i in keys:
        pydirectinput.keyDown(i, _pause=False)
        time.sleep(0.08)
        pydirectinput.keyUp(i, _pause=False)
        time.sleep(0.08)

def clean_keys() -> None:
    """
    'Lifts' each key that was pressed previously.

    Args:
        None

    Returns:
        None
    """
    try:
        for i in PREV_ACTION:
            pydirectinput.keyUp(i, _pause=False)
        PREV_ACTION.clear()
    except:
        print("Error in clean_keys()")

def press_combos(keys: list) -> None:
    """
    Function used to 'press' down multiple keys at the same time

    Args:
        key: the list of keys to press

    Returns:
        None
    """
    clean_keys()
    for i in keys:
        if i == '':
            continue
        pydirectinput.keyDown(i, _pause=False)
        PREV_ACTION.append(i)

def key_press(key: str, t: float = 0.1) -> None:
    """
    Function used to 'press' key down for period of time

    Args:
        key: the string of the key that is being pressed
        t: the time in seconds to press the key

    Returns:
        None
    """
    pydirectinput.keyDown(key, _pause=False)
    time.sleep(t)
    pydirectinput.keyUp(key, _pause=False)
    time.sleep(0.08)

def press_controller_button(button):
    controller.press_button(button)
    controller.update()
    time.sleep(0.06)
    controller.release_button(button)
    controller.update()

def rapid_fire_button(button, times):
    for _ in range(times):
        controller.press_button(button)
        controller.update()
        controller.release_button(button)
        controller.update()

def press_controller_direction(button):
    controller.directional_pad(button)
    controller.update()
    time.sleep(0.06)
    controller.directional_pad(vg.DS4_DPAD_DIRECTIONS.DS4_BUTTON_DPAD_NONE)
    controller.update()

def press_controller_special(button):
    controller.press_special_button(button)
    controller.update()
    time.sleep(0.06)
    controller.release_special_button(button)
    controller.update()

def enter_boss() -> None:
    """
    General function used to enter the fog wall

    Args:
        None

    Returns:
        None
    """
    key_press('e')
    key_press('e')
    time.sleep(4)
    key_press('w', 0.6)

def lock_on() -> None:
    key_press('q')

def travel_to_roundtable():
    find_activate_window()
    time.sleep(0.2)
    key_press('g')
    time.sleep(1)
    key_press('f')
    time.sleep(0.2)
    key_press('r')
    time.sleep(0.3)
    key_press('e')
    time.sleep(12)

def talk_to_gideon(slots: list) -> None:
    find_activate_window()
    time.sleep(2)
    key_press('e')
    time.sleep(0.6)
    key_press('e')
    time.sleep(0.2)
    for i in slots:
        key_presses(['down'] * i)
        time.sleep(0.08)
        key_press('e')
        time.sleep(0.2)
    key_press('e')
    time.sleep(12)