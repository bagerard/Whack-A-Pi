# Whack-A-Pi

This is an enhanced version of the game described in this excellent blog post https://fortoffee.org.uk/2016/03/whack-a-pi/

Main features that were added:
- Store all players scores, not only highest scores
- Store additional metadata per game (latest game timestamp, mean hit time, number of games)
- Add a 'HiScore' & 'Recent Players' screen

## Install
Make sure you have pyenv installed, then run:

    make setup-venv

## Run
Simply run:

    python main.py

And if you don't have a raspberry Pi plugged in, you can mock the GPIO device with:

    GPIOZERO_PIN_FACTORY=mock python main.py

The start-up position of the window can be provided with for instance:
    
    SDL_VIDEO_WINDOW_POS=10,10

For testing/troubleshooting purposes, it is possible to launch a thread that will trigger the buttons in a loop,
this allows for testing without a Pi. Use `BUTTON_THREAD=1` env var to turn this on. The following is what I typically
use for development:

    GPIOZERO_PIN_FACTORY=mock BUTTON_THREAD=1 python main.py

In case a button breaks or is not available, it is also possible to remove it from the game
by its index (starting at 0) with for instance:

    DISABLED_BTN=4

And the following is what I use when it runs on the Pi with the external monitor plugged in:

    SDL_VIDEO_WINDOW_POS=0,0 python main.py

## Credits
The LED Clock (or 7 segment style) font is called Digital 7 and is freeware available from styleseven.com