import keyboard

def on_press(event):
    print(f'Key {event.name} pressed')

keyboard.on_press(on_press)

while True:
    pass