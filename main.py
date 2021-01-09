import simpleaudio
import json
import time
import mouse_controller
import keyboard
import mouse
import os

PATH_TO_THIS_FILE = os.path.dirname(__file__)

mouse_values = {}
keys_values = {}
_pause = False
_insert_mode = False
_insert_mode_temp = False

_increase_step = 2
_gravity_step = 10
_max_value = 200
_min_value = 0

move_step = 1
gravity_step = 2
max_value = 100

enter_sound = simpleaudio.WaveObject.from_wave_file(os.path.join(PATH_TO_THIS_FILE, 'inputmode_enter.wav'))
exit_sound = simpleaudio.WaveObject.from_wave_file(os.path.join(PATH_TO_THIS_FILE, 'inputmode_exit.wav'))

play_buffer = None

Key = {
    'Up': 'k',
    'Down': 'j',
    'Left': 'h',
    'Right': 'l',
    'LeftMouse': 'u',
    'RightMouse': 'y',
    'MiddleMouse': ';',
    'ScrollUp': 't',
    'ScrollDown': 'g',
    'InsertMode': '`',
    'ExitInsertMode': 'esc'
}

def move():
    Y = keys_values[Key['Down']] - keys_values[Key['Up']]
    X = keys_values[Key['Right']] - keys_values[Key['Left']]
    mouse_controller.MouseMoveTo([int(X), int(Y)])

def scroll():
    delta = keys_values[Key['ScrollUp']] - keys_values[Key['ScrollDown']]
    mouse.wheel(delta)

def set_pause(pause_keys, insert_mode):
    global _insert_mode
    if _insert_mode == insert_mode: return
    _insert_mode = insert_mode

def check_pause():
    global _insert_mode, _insert_mode_temp
    if not keyboard.is_pressed(Key['ExitInsertMode']) and _insert_mode != _insert_mode_temp:
        _insert_mode_temp = _insert_mode
        if _insert_mode:
            keyboard.block_key(Key['ExitInsertMode'])
            for name in Key:
                if name != 'ExitInsertMode':
                    keyboard.unblock_key(Key[name])
            play_buffer = enter_sound.play()
        else:
            keyboard.unblock_key(Key['ExitInsertMode'])
            for name in Key:
                if name != 'ExitInsertMode':
                    keyboard.block_key(Key[name])
            play_buffer = exit_sound.play()



def check_acceleration(hardware, key, increase_step, gravity_step, max_value, min_value, foo1, foo2):
    global mouse_values, keys_values
    values = {}

    if hardware == mouse:
        values = mouse_values
    elif hardware == keyboard:
        values = keys_values

    if key not in values:
        values[key] = 0


    if hardware.is_pressed(key):
        values[key] = max(min(values[key] + increase_step, max_value), min_value)
        if callable(foo1):
            foo1(type(values[key]))
    else:
        values[key] = max(min(values[key] - gravity_step, max_value), min_value)
        if callable(foo2):
            foo2(type(values[key]))

    if hardware == mouse:
        mouse_values = values
    elif hardware == keyboard:
        keys_values = values


def check_click(hardware, key, function_1, function_2, args1, args2):
    global mouse_values, keys_values
    values = {}

    if hardware == mouse:
        values = mouse_values
    elif hardware == keyboard:
        values = keys_values

    if key not in values:
        values[key] = 0

    if hardware.is_pressed(key) and values[key] == 0:
        values[key] = 1
        if callable(function_1):
            function_1(*args1)
    elif not hardware.is_pressed(key) and values[key] == 1:
        values[key] = 0
        if callable(function_2):
            function_2(*args2)

    if hardware == mouse:
        mouse_values = values
    elif hardware == keyboard:
        keys_values = values

def awake():
    for name in Key:
        keys_values[Key[name]] = 0

    for name in Key:
        if name != 'ExitInsertMode':
            keyboard.block_key(Key[name])
    pass

def move_cursor(increase_step = _increase_step, gravity_step = _gravity_step, min_value = _min_value, max_value = _max_value):
    check_acceleration(keyboard, Key['Up'], increase_step, gravity_step, max_value, min_value, None, None)
    check_acceleration(keyboard, Key['Down'], increase_step, gravity_step, max_value, min_value, None, None)
    check_acceleration(keyboard, Key['Left'], increase_step, gravity_step, max_value, min_value, None, None)
    check_acceleration(keyboard, Key['Right'], increase_step, gravity_step, max_value, min_value, None, None)

def mouse_clicks():
    check_click(keyboard, Key['LeftMouse'], mouse.press, mouse.release, [mouse.LEFT], [mouse.LEFT])
    check_click(keyboard, Key['RightMouse'], mouse.press, mouse.release, [mouse.RIGHT], [mouse.RIGHT])
    check_click(keyboard, Key['MiddleMouse'], mouse.press, mouse.release, [mouse.MIDDLE], [mouse.MIDDLE])

def mouse_scrolls():
    check_acceleration(keyboard, Key['ScrollUp'], 0.1, 0.1, 1, 0, None, None)
    check_acceleration(keyboard, Key['ScrollDown'], 0.1, 0.1, 1, 0, None, None)

def update():
    global _insert_mode
    # print(keys_values)
    check_click(keyboard, Key['InsertMode'], set_pause, None, [[Key['ExitInsertMode']], True], [])
    check_click(keyboard, Key['ExitInsertMode'], set_pause, None, [[Key['ExitInsertMode']], False], [])
    check_pause()
    if not _insert_mode:
        move_cursor()
        mouse_clicks()
        mouse_scrolls()
        move()
        scroll()
    pass


if __name__ == '__main__':
    awake()
    while True:
        time.sleep(0.01)
        update()
