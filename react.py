from gpiozero import LEDBoard, Button
import time
from random import randint
from threading import Thread, Event


class Game:
    def __init__(self):
        self.lights = LEDBoard(2, 3, 4, 14, 15, 17, 18, 27, 22, 23, 24, 10, 9)
        self.buttons = [
            Button(25),
            Button(11),
            Button(8),
            Button(7),
            Button(5),
            Button(6),
            Button(12),
            Button(13),
            Button(19),
            Button(16),
            Button(26),
            Button(20),
            Button(21),
        ]
        self.start_time = 0
        self.score = 0
        self.game_thread = None
        self.idle_thread = None
        self.idle_stop = Event()
        self.game_stop = Event()
        self.current_idx = -1

    def start_loop_btn_thread(self):
        def _loop_btn(buttons):
            while True:
                for btn in buttons:
                    print(f'push button {btn}')
                    btn.pin.drive_low()
                    print(f'release button {btn}')
                    btn.pin.drive_high()
                    time.sleep(1)
        print('start start_loop_btn_thread')
        Thread(target=_loop_btn, args=(self.buttons,)).start()

    @property
    def n_leds(self):
        return len(self.lights.leds)

    def button_test(self):
        print("button test")
        self.lights.on()
        time.sleep(5)
        self.lights.off()

        for idx in range(0, self.n_leds):
            print(self.lights.leds[idx].pin.number)
            self.lights.leds[idx].on()
            self.buttons[idx].wait_for_press(30)
            self.lights.leds[idx].off()

    def elapsed_time(self):
        return time.time() - self.start_time

    def wait_for_press(self, idx, delay=-1):
        print("wait_for_press")
        wait_start = time.time()
        while not self.game_stop.isSet():
            if self.buttons[idx].is_pressed:
                return True
            if time.time() - wait_start >= delay:
                break
        return False

    def ready_wait(self, delay):
        print('ready_wait')
        self.lights.off()
        btn_idx = 3
        led = self.lights.leds[btn_idx]
        btn = self.buttons[btn_idx]

        print(f'Light on {led}')
        led.on()
        print(f'Waiting for {btn}...')
        btn_pressed = btn.wait_for_press(delay)

        led.off()
        print('btn_pressed')
        return btn_pressed

    def start_game(self):
        print("start_game")
        self.game_stop.clear()
        self.game_thread = Thread(target=self._rungame)
        self.start_time = time.time()
        self.game_thread.start()

    def stop_game(self):
        print("stop_game")
        self.buttons[self.current_idx].close()
        self.game_stop.set()
        self.game_thread.join()

    def _rungame(self):
        print("_rungame")
        elapsed = 0
        last_idx = -1
        self.score = 0
        while elapsed < 60 and not self.game_stop.isSet():
            # Find a button that is not the last one
            while last_idx == self.current_idx:
                self.current_idx = randint(0, self.n_leds - 1)

            led = self.lights.leds[self.current_idx]
            btn = self.buttons[self.current_idx]

            led.on()

            delay = max(0, 60 - self.elapsed_time())
            # print(delay)

            print(f'run game, waiting on {btn}')
            if btn.wait_for_press(delay):
                self.score += 1

            led.off()

            last_idx = self.current_idx
            elapsed = self.elapsed_time()
        # print ("Time up")
        # print("Score:", score)

    def start_idle(self):
        self.idle_stop.clear()
        self.idle_thread = Thread(target=self._idle)
        self.idle_thread.start()

    def stop_idle(self):
        self.idle_stop.set()
        self.idle_thread.join()

    def _idle(self):
        max_patterns = 4
        rows = [[0, 1], [2, 3, 4], [5, 6, 7, 8], [9, 10, 11], [12]]
        cols = [[5], [0, 2, 9], [6], [3, 10, 12], [7], [1, 4, 11], [8]]
        pulse = [[6, 7], [3, 10], [2, 4, 9, 11], [5, 8], [0, 1, 12]]

        idle_pattern = 3
        while not self.idle_stop.isSet():
            idle_pattern = randint(0, max_patterns)
            # idle_pattern += 1
            if idle_pattern > max_patterns:
                break

            self.lights.off()
            seq_start = time.time()

            if idle_pattern == 0:
                while time.time() - seq_start < 5 and not self.idle_stop.isSet():
                    self.lights.leds[randint(0, self.n_leds - 1)].toggle()
                    self.idle_stop.wait(0.1)

            if idle_pattern == 1:
                for i in range(0, 2):
                    count = 0
                    while count < self.n_leds and not self.idle_stop.isSet():
                        self.lights.leds[count].toggle()
                        count += 1
                        self.idle_stop.wait(0.25)

            if idle_pattern == 2:
                self.lights.blink(on_time=0.5, off_time=0.5, background=True)
                while time.time() - seq_start < 5 and not self.idle_stop.isSet():
                    pass
                self.lights.off()

            if idle_pattern == 3:
                delay = 0.5
                for i in range(0, 2):
                    for r in rows:
                        for idx in r:
                            self.lights.leds[idx].on()
                        self.idle_stop.wait(delay)
                        for idx in r:
                            self.lights.leds[idx].off()

                    if not self.idle_stop.isSet():
                        for c in cols:
                            for idx in c:
                                self.lights.leds[idx].on()
                            self.idle_stop.wait(delay)
                            for idx in c:
                                self.lights.leds[idx].off()

            if idle_pattern == 4:
                delay = 0.5
                for i in range(0, 2):
                    for group in pulse:
                        for idx in group:
                            self.lights.leds[idx].on()
                        self.idle_stop.wait(delay)
                        for idx in group:
                            self.lights.leds[idx].off()

        self.lights.off()
