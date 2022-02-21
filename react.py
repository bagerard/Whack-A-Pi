import time
from dataclasses import dataclass, field
from random import randint
from threading import Thread, Event
from contextlib import contextmanager
from typing import List
import statistics

from gpiozero import LEDBoard, Button


DEFAULT_HIT_TIME = 10.0
READY_BTN_IDX = 7


@contextmanager
def light_on_led(led):
    print(f"Light on LED {led.pin.number}")
    led.on()
    try:
        yield
    finally:
        print(f"Light off LED {led.pin.number}")
        led.off()


def compute_score_increment(time_to_hit: float):
    # MAX_HIT_SCORE = 5
    # rounded_hit_time = math.floor(time_to_hit)
    # return max(MAX_HIT_SCORE - rounded_hit_time, 1)
    return 5  # Simplify it


@dataclass
class GameResult:
    score: int = 0
    response_times: List[float] = field(default_factory=list)

    def register_new_hit(self, hit_time: float):
        self.score += compute_score_increment(hit_time)
        self.response_times.append(hit_time)

    @property
    def mean_hit_time(self):
        if self.response_times:
            return statistics.mean(self.response_times)
        else:
            return DEFAULT_HIT_TIME

    @property
    def n_hits(self):
        return len(self.response_times)


class GameEngine:
    def __init__(self, game_time: int, disabled_btn_idx: int = None):
        self.game_time = game_time

        led_gpios = [2, 3, 4, 14, 15, 17, 18, 27, 22, 23, 24, 10, 9]

        button_gpios = [
            25,
            11,
            8,
            7,
            5,
            6,
            12,
            13,
            19,
            16,
            26,
            20,
            21,
        ]

        if disabled_btn_idx is not None:
            print(
                f"Disabling button/led idx: {disabled_btn_idx} (b{button_gpios[disabled_btn_idx]}, l{led_gpios[disabled_btn_idx]}) "
            )
            del led_gpios[disabled_btn_idx]
            del button_gpios[disabled_btn_idx]

        self.lights = LEDBoard(*led_gpios)
        self.buttons = [Button(gpio_idx) for gpio_idx in button_gpios]

        self.start_time = 0
        self.game_result = GameResult()
        self.game_thread = None
        self.idle_thread = None
        self.idle_stop = Event()
        self.game_stop = Event()
        self.current_idx = -1

    def _get_button_led(self, idx):
        return self.buttons[idx], self.lights[idx]

    def start_loop_btn_thread(self):
        """
        WHILE WAITING FOR BUTTONS AND PI
        """

        def _loop_btn(buttons):
            print("Start dirty loop that press buttons...")
            while not self.game_stop.isSet():
                for btn in buttons:
                    print(f"push button {btn.pin.number}")
                    btn.pin.drive_low()
                    btn.pin.drive_high()
                    time.sleep(0.5)

        print("start start_loop_btn_thread")
        Thread(target=_loop_btn, args=(self.buttons,)).start()

    @property
    def n_leds(self):
        return len(self.lights.leds)

    def button_test(self, wait_for_press_time=5):
        print("button test")
        self.lights.on()
        time.sleep(3)
        self.lights.off()

        for idx in range(0, self.n_leds):
            btn, led = self._get_button_led(idx)
            with light_on_led(led):
                btn.wait_for_press(wait_for_press_time)

    def elapsed_time(self):
        return time.time() - self.start_time

    def ready_wait(self, delay):
        print("ready_wait")
        self.lights.off()

        btn, led = self._get_button_led(READY_BTN_IDX)

        with light_on_led(led):
            print(f"Waiting on {btn.pin.number}")
            btn_pressed = btn.wait_for_press(delay)

        print("btn_pressed")
        return btn_pressed

    def start_game(self):
        print("start_game")
        self.game_stop.clear()
        self.game_thread = Thread(target=self._run_game)
        self.start_time = time.time()
        self.game_thread.start()

    def stop_game(self):
        print("stop_game")
        self.buttons[self.current_idx].close()
        self.game_stop.set()
        if self.game_thread is not None:
            self.game_thread.join()

    def _run_game(self):
        print("_run_game")
        elapsed = 0
        last_idx = -1
        self.game_result = GameResult()

        self.user_response_time = []

        while elapsed < self.game_time and not self.game_stop.isSet():

            # Pick a button that is not the current one
            while last_idx == self.current_idx:
                self.current_idx = randint(0, self.n_leds - 1)

            btn, led = self._get_button_led(self.current_idx)

            with light_on_led(led):
                start = time.time()
                delay = max(0, self.game_time - self.elapsed_time())
                print(f"--> run game, waiting on {btn.pin.number}...")
                if btn.wait_for_press(delay):
                    time_to_press = time.time() - start
                    self.game_result.register_new_hit(time_to_press)

            last_idx = self.current_idx
            elapsed = self.elapsed_time()

    def start_idle(self):
        self.idle_stop.clear()
        self.idle_thread = Thread(target=self._idle)
        self.idle_thread.start()

    def stop_idle(self):
        self.idle_stop.set()
        self.idle_thread.join()

    def _idle(self):
        max_patterns = 4

        def safe_idx(idx_arrays):
            # remove non-existing idx (if any)
            for i, _ in enumerate(idx_arrays):
                idx_arrays[i] = [idx for idx in idx_arrays[i] if idx < self.n_leds]
            return idx_arrays

        rows = safe_idx([[0, 12], [1, 2, 11], [3, 7, 10], [4], [5, 9], [6, 8]])
        cols = safe_idx([[6, 5, 4, 3, 0], [2, 1], [7], [8, 9, 10, 11, 12]])
        pulse = safe_idx([[6, 12], [8, 0], [4, 5, 9, 10], [1, 2, 3, 7, 11]])

        while not self.idle_stop.isSet():
            idle_pattern = randint(0, max_patterns)

            if idle_pattern > max_patterns:
                break

            self.lights.off()
            seq_start = time.time()

            if idle_pattern == 0:
                while time.time() - seq_start < 5 and not self.idle_stop.isSet():
                    self.lights[randint(0, self.n_leds - 1)].toggle()
                    self.idle_stop.wait(0.1)

            if idle_pattern == 1:
                for i in range(0, 2):
                    count = 0
                    while count < self.n_leds and not self.idle_stop.isSet():
                        self.lights[count].toggle()
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
