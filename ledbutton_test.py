"""
Allows to test all buttons + leds
It will light on all the buttons, 1 by 1, waiting for push
"""
from react import GameEngine

# # Mock GPIO
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory
#
# Device.pin_factory = MockFactory()
# #

if __name__ == "__main__":
    game_engine = GameEngine(999)
    game_engine.button_test()
