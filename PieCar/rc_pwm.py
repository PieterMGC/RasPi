# rc_pwm.py
from __future__ import annotations
import time
import lgpio
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class ChannelReading:
    us: Optional[float]        # pulse width in microseconds (None if failsafe)
    norm: Optional[float]      # -1..+1 (None if failsafe)
    age_s: float               # seconds since last valid pulse


class RcPwmReader:
    """
    Reads PWM from RC receiver channels via lgpio alerts.
    - One GPIO per channel (PWM)
    - Provides pulse width (us) and normalized (-1..+1)
    """

    def __init__(
        self,
        channels: Dict[str, int],       # e.g. {"steer":22, "throttle":27}
        center_us: float = 1500.0,
        span_us: float = 500.0,
        dead_us: float = 30.0,
        failsafe_s: float = 0.2,
        gpiochip: int = 0,
    ):
        self.channels = channels
        self.center_us = center_us
        self.span_us = span_us
        self.dead_us = dead_us
        self.failsafe_s = failsafe_s

        self._h = lgpio.gpiochip_open(gpiochip)
        self._state = {}   # pin -> dict
        self._callbacks = []  # keep handles alive

        # Setup pins
        for name, pin in self.channels.items():
            lgpio.gpio_claim_alert(self._h, pin, lgpio.BOTH_EDGES)
            self._state[pin] = {"rise": None, "last_us": None, "last_t": 0.0}

        # One callback function for all pins
        def _cb(chip, gpio, level, tick):
            s = self._state.get(gpio)
            if s is None:
                return
            if level == 1:
                s["rise"] = tick
            elif level == 0 and s["rise"] is not None:
                s["last_us"] = (tick - s["rise"]) / 1000.0
                s["last_t"] = time.monotonic()
                s["rise"] = None

        for _, pin in self.channels.items():
            self._callbacks.append(lgpio.callback(self._h, pin, lgpio.BOTH_EDGES, _cb))

    def close(self):
        """Release gpiochip handle."""
        try:
            if self._h is not None:
                lgpio.gpiochip_close(self._h)
        finally:
            self._h = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    @staticmethod
    def _clamp(x: float, lo: float, hi: float) -> float:
        return lo if x < lo else hi if x > hi else x

    def _norm_from_us(self, us: float) -> float:
        d = us - self.center_us
        if abs(d) < self.dead_us:
            d = 0.0
        return self._clamp(d / self.span_us, -1.0, 1.0)

    def read(self, name: str) -> ChannelReading:
        """Read one channel by name."""
        pin = self.channels[name]
        s = self._state[pin]
        now = time.monotonic()

        if s["last_us"] is None:
            return ChannelReading(us=None, norm=None, age_s=float("inf"))

        age = now - s["last_t"]
        if age > self.failsafe_s:
            return ChannelReading(us=None, norm=None, age_s=age)

        us = float(s["last_us"])
        return ChannelReading(us=us, norm=self._norm_from_us(us), age_s=age)

    def read_all(self) -> Dict[str, ChannelReading]:
        """Read all channels."""
        return {name: self.read(name) for name in self.channels.keys()}
