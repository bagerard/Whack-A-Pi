from react import GameEngine

# # Mock GPIO
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory
#
# Device.pin_factory = MockFactory()
# #

game_engine = GameEngine(999)
game_engine.button_test()
