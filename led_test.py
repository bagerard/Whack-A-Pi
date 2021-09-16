import time
from react import GameEngine

# Mock GPIO
from gpiozero import Device
from gpiozero.pins.mock import MockFactory

Device.pin_factory = MockFactory()
#

game_engine = GameEngine(999)
while True:
    game_engine.lights.on()
    time.sleep(1)
    game_engine.lights.off()
