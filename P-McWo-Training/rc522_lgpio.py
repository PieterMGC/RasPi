# rc522_lgpio.py
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, Tuple, List

import spidev
import lgpio


@dataclass(frozen=True)
class TagEvent:
    uid_bytes: Tuple[int, int, int, int]
    uid_hex: str
    tag_type: int


class RC522Spi:
    # ---- RC522 registers ----
    CommandReg       = 0x01
    CommIEnReg       = 0x02
    CommIrqReg       = 0x04
    DivIrqReg        = 0x05
    ErrorReg         = 0x06
    FIFODataReg      = 0x09
    FIFOLevelReg     = 0x0A
    ControlReg       = 0x0C
    BitFramingReg    = 0x0D
    CollReg          = 0x0E

    ModeReg          = 0x11
    TxControlReg     = 0x14
    TxASKReg         = 0x15
    TModeReg         = 0x2A
    TPrescalerReg    = 0x2B
    TReloadRegH      = 0x2C
    TReloadRegL      = 0x2D

    VersionReg       = 0x37

    # ---- RC522 commands ----
    PCD_IDLE         = 0x00
    PCD_CALCCRC      = 0x03
    PCD_TRANSCEIVE   = 0x0C
    PCD_SOFTRESET    = 0x0F

    # ---- PICC commands ----
    PICC_REQA        = 0x26  # 7-bit request
    PICC_WUPA        = 0x52  # 7-bit wakeup (often more reliable)
    PICC_ANTICOLL    = 0x93

    MI_OK            = 0
    MI_NOTAGERR      = 1
    MI_ERR           = 2

    def __init__(self, spi_bus: int = 0, spi_dev: int = 0, spi_speed: int = 200_000):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_dev)
        self.spi.mode = 0
        self.spi.max_speed_hz = spi_speed

    def close(self) -> None:
        try:
            self.spi.close()
        except Exception:
            pass

    def _wreg(self, addr: int, val: int) -> None:
        self.spi.xfer2([((addr << 1) & 0x7E), val & 0xFF])

    def _rreg(self, addr: int) -> int:
        return self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0x00])[1]

    def _set_bits(self, addr: int, mask: int) -> None:
        self._wreg(addr, self._rreg(addr) | mask)

    def _clear_bits(self, addr: int, mask: int) -> None:
        self._wreg(addr, self._rreg(addr) & (~mask & 0xFF))

    def soft_reset(self) -> None:
        self._wreg(self.CommandReg, self.PCD_SOFTRESET)
        time.sleep(0.05)

    def init(self) -> None:
        self.soft_reset()

        # Common MFRC522 init values
        self._wreg(self.TModeReg, 0x8D)
        self._wreg(self.TPrescalerReg, 0x3E)
        self._wreg(self.TReloadRegL, 30)
        self._wreg(self.TReloadRegH, 0)
        self._wreg(self.TxASKReg, 0x40)
        self._wreg(self.ModeReg, 0x3D)

        # Clear collision bit (some clones misbehave otherwise)
        self._clear_bits(self.CollReg, 0x80)

        self.antenna_on()

    def antenna_on(self) -> None:
        if (self._rreg(self.TxControlReg) & 0x03) != 0x03:
            self._set_bits(self.TxControlReg, 0x03)

    def antenna_off(self) -> None:
        self._clear_bits(self.TxControlReg, 0x03)

    def _to_card(self, command: int, send_data: List[int]) -> Tuple[int, List[int], int]:
        back_data: List[int] = []
        back_bits = 0

        irq_en = 0x00
        wait_irq = 0x00
        if command == self.PCD_TRANSCEIVE:
            irq_en = 0x77
            wait_irq = 0x30

        self._wreg(self.CommIEnReg, irq_en | 0x80)
        self._clear_bits(self.CommIrqReg, 0x80)
        self._set_bits(self.FIFOLevelReg, 0x80)
        self._wreg(self.CommandReg, self.PCD_IDLE)

        for b in send_data:
            self._wreg(self.FIFODataReg, b)

        self._wreg(self.CommandReg, command)
        if command == self.PCD_TRANSCEIVE:
            self._set_bits(self.BitFramingReg, 0x80)  # StartSend

        # Wait for completion or timeout
        for _ in range(2000):
            n = self._rreg(self.CommIrqReg)
            if n & wait_irq:
                break
            if n & 0x01:  # timer irq
                self._clear_bits(self.BitFramingReg, 0x80)
                return (self.MI_NOTAGERR, [], 0)

        self._clear_bits(self.BitFramingReg, 0x80)

        err = self._rreg(self.ErrorReg)
        if (err & 0x1B) != 0:
            return (self.MI_ERR, [], 0)

        fifo_level = self._rreg(self.FIFOLevelReg)
        last_bits = self._rreg(self.ControlReg) & 0x07
        if last_bits:
            back_bits = (fifo_level - 1) * 8 + last_bits
        else:
            back_bits = fifo_level * 8

        for _ in range(fifo_level):
            back_data.append(self._rreg(self.FIFODataReg))

        return (self.MI_OK, back_data, back_bits)

    def request(self, wakeup: bool = True) -> Tuple[int, Optional[int]]:
        # REQA/WUPA is 7 bits
        self._wreg(self.BitFramingReg, 0x07)
        cmd = self.PICC_WUPA if wakeup else self.PICC_REQA
        status, back_data, back_bits = self._to_card(self.PCD_TRANSCEIVE, [cmd])

        if status != self.MI_OK or back_bits != 0x10 or not back_data:
            return (self.MI_NOTAGERR, None)

        return (self.MI_OK, back_data[0])

    def anticoll(self) -> Tuple[int, Optional[Tuple[int, int, int, int]]]:
        self._wreg(self.BitFramingReg, 0x00)
        status, back_data, _ = self._to_card(self.PCD_TRANSCEIVE, [self.PICC_ANTICOLL, 0x20])

        if status != self.MI_OK or len(back_data) < 5:
            return (self.MI_ERR, None)

        uid5 = back_data[:5]
        bcc = uid5[0] ^ uid5[1] ^ uid5[2] ^ uid5[3]
        if bcc != uid5[4]:
            return (self.MI_ERR, None)

        return (self.MI_OK, (uid5[0], uid5[1], uid5[2], uid5[3]))


class RC522Reader:
    """
    Pi-5-safe RC522 reader:
    - SPI via spidev
    - Reset pin via lgpio (no RPi.GPIO)
    - Provides non-blocking poll() that returns TagEvent or None
    - Has self-heal reset/re-init if no tags are seen for a while
    """

    def __init__(
        self,
        spi_bus: int = 0,
        spi_dev: int = 0,
        spi_speed: int = 200_000,
        rst_gpio: int = 25,
        gpiochip: int = 0,
        reset_idle_s: float = 1.0,
        wakeup: bool = True,
    ):
        self.spi_bus = spi_bus
        self.spi_dev = spi_dev
        self.spi_speed = spi_speed
        self.rst_gpio = rst_gpio
        self.gpiochip = gpiochip
        self.reset_idle_s = reset_idle_s
        self.wakeup = wakeup

        self._h = lgpio.gpiochip_open(gpiochip)
        lgpio.gpio_claim_output(self._h, rst_gpio, 1)

        self._rc = None  # type: Optional[RC522Spi]
        self._last_any_ts = time.time()

        self._open()

    def _open(self) -> None:
        self._hw_reset()
        self._rc = RC522Spi(self.spi_bus, self.spi_dev, self.spi_speed)
        self._rc.init()
        self._last_any_ts = time.time()

    def _hw_reset(self) -> None:
        lgpio.gpio_write(self._h, self.rst_gpio, 0)
        time.sleep(0.05)
        lgpio.gpio_write(self._h, self.rst_gpio, 1)
        time.sleep(0.05)

    def close(self) -> None:
        if self._rc is not None:
            self._rc.antenna_off()
            self._rc.close()
            self._rc = None
        try:
            lgpio.gpiochip_close(self._h)
        except Exception:
            pass

    def __enter__(self) -> "RC522Reader":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @staticmethod
    def _uid_hex(uid: Tuple[int, int, int, int]) -> str:
        return ":".join(f"{b:02X}" for b in uid)

    def poll(self) -> Optional[TagEvent]:
        """
        Non-blocking: returns TagEvent if a tag is detected, else None.
        Self-heals if idle for reset_idle_s.
        """
        if self._rc is None:
            return None

        # self-heal on idle (addresses "works only if tag at startup" behavior)
        if (time.time() - self._last_any_ts) > self.reset_idle_s:
            try:
                self._rc.antenna_off()
                self._rc.close()
            except Exception:
                pass
            self._open()

        st, tag_type = self._rc.request(wakeup=self.wakeup)
        if st != RC522Spi.MI_OK or tag_type is None:
            return None

        st2, uid = self._rc.anticoll()
        if st2 != RC522Spi.MI_OK or uid is None:
            return None

        self._last_any_ts = time.time()
        return TagEvent(uid_bytes=uid, uid_hex=self._uid_hex(uid), tag_type=tag_type)
