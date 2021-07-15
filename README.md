# Whack-A-Pi

This is an enhanced version of the game described in this excellent blog post https://fortoffee.org.uk/2016/03/whack-a-pi/

Main features that were added:
- Store all players scores, not only high scorers
- Store additional metadata per game (latest game timestamp, mean hit time, number of games)
- Add a HiScore screen

The game is currently set up to launch a thread that will trigger the buttons in a loop, this allows for testing
while I'm waiting for the delivery of the arcade buttons

## Install
Make sure you have pyenv installed, then run:

    make setup-venv

## Run
Simply run:

    python main.py

And if you don't have a raspberry Pi plugged in, you can mock the GPIO device with:

    GPIOZERO_PIN_FACTORY=mock python main.py
    
## Credits
The LED Clock (or 7 segment style) font is called Digital 7 and is freeware available from styleseven.com