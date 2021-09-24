"""
Allows to test all ledgs
It will light all leds
"""
import time
from react import GameEngine

# # Mock GPIO
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory
#
# Device.pin_factory = MockFactory()
# #

if __name__ == "__main__":
    game_engine = GameEngine(999)
    while True:
        game_engine.lights.on()
        time.sleep(10)
        game_engine.lights.off()
        time.sleep(1)
