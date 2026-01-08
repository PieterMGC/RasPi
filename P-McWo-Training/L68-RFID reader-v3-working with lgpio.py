import time
import spidev
import lgpio


class RC522:
    # ---- RC522 registers ----
    CommandReg       = 0x01
    CommIEnReg       = 0x02
    DivIEnReg        = 0x03
    CommIrqReg       = 0x04
    DivIrqReg        = 0x05
    ErrorReg         = 0x06
    Status1Reg       = 0x07
    Status2Reg       = 0x08
    FIFODataReg      = 0x09
    FIFOLevelReg     = 0x0A
    ControlReg       = 0x0C
    BitFramingReg    = 0x0D
    CollReg          = 0x0E

    ModeReg          = 0x11
    TxModeReg        = 0x12
    RxModeReg        = 0x13
    TxControlReg     = 0x14
    TxASKReg         = 0x15
    CRCResultRegM    = 0x21
    CRCResultRegL    = 0x22
    TModeReg         = 0x2A
    TPrescalerReg    = 0x2B
    TReloadRegH      = 0x2C
    TReloadRegL      = 0x2D

    VersionReg       = 0x37

    # ---- RC522 commands ----
    PCD_IDLE         = 0x00
    PCD_MEM          = 0x01
    PCD_CALCCRC      = 0x03
    PCD_TRANSCEIVE   = 0x0C
    PCD_SOFTRESET    = 0x0F

    # ---- PICC commands ----
    PICC_REQIDL      = 0x26  # REQA (7 bits)
    PICC_ANTICOLL    = 0x93  # anticollision cascade level 1

    MI_OK            = 0
    MI_NOTAGERR      = 1
    MI_ERR           = 2

    def __init__(self, spi_bus=0, spi_dev=0, spi_speed=200_000):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_dev)
        self.spi.mode = 0
        self.spi.max_speed_hz = spi_speed

    def close(self):
        self.spi.close()

    # -------- low-level register ops ----------
    def _wreg(self, addr: int, val: int) -> None:
        self.spi.xfer2([((addr << 1) & 0x7E), val & 0xFF])

    def _rreg(self, addr: int) -> int:
        return self.spi.xfer2([((addr << 1) & 0x7E) | 0x80, 0x00])[1]

    def _set_bits(self, addr: int, mask: int) -> None:
        self._wreg(addr, self._rreg(addr) | mask)

    def _clear_bits(self, addr: int, mask: int) -> None:
        self._wreg(addr, self._rreg(addr) & (~mask & 0xFF))

    # -------- init / antenna ----------
    def soft_reset(self):
        self._wreg(self.CommandReg, self.PCD_SOFTRESET)
        time.sleep(0.05)

    def init(self):
        self.soft_reset()

        # Timer: recommended init values (common in MFRC522 libs)
        self._wreg(self.TModeReg, 0x8D)
        self._wreg(self.TPrescalerReg, 0x3E)
        self._wreg(self.TReloadRegL, 30)
        self._wreg(self.TReloadRegH, 0)

        self._wreg(self.TxASKReg, 0x40)     # force 100% ASK
        self._wreg(self.ModeReg, 0x3D)      # CRC preset 0x6363

        self.antenna_on()

    def antenna_on(self):
        tx = self._rreg(self.TxControlReg)
        if (tx & 0x03) != 0x03:
            self._set_bits(self.TxControlReg, 0x03)

    def antenna_off(self):
        self._clear_bits(self.TxControlReg, 0x03)

    # -------- CRC ----------
    def _calc_crc(self, data: list[int]) -> list[int]:
        self._clear_bits(self.DivIrqReg, 0x04)
        self._set_bits(self.FIFOLevelReg, 0x80)

        for b in data:
            self._wreg(self.FIFODataReg, b)

        self._wreg(self.CommandReg, self.PCD_CALCCRC)

        # Wait for CRC completion
        for _ in range(5000):
            n = self._rreg(self.DivIrqReg)
            if n & 0x04:
                break
        return [self._rreg(self.CRCResultRegL), self._rreg(self.CRCResultRegM)]

    # -------- card comm ----------
    def _to_card(self, command: int, send_data: list[int]) -> tuple[int, list[int], int]:
        back_data: list[int] = []
        back_bits = 0
        status = self.MI_ERR

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

        # wait for completion
        i = 2000
        while i > 0:
            n = self._rreg(self.CommIrqReg)
            if n & wait_irq:
                break
            if n & 0x01:  # timer irq
                return (self.MI_NOTAGERR, [], 0)
            i -= 1

        self._clear_bits(self.BitFramingReg, 0x80)

        err = self._rreg(self.ErrorReg)
        if (err & 0x1B) == 0:
            status = self.MI_OK

            if n & 0x01:
                status = self.MI_NOTAGERR

            fifo_level = self._rreg(self.FIFOLevelReg)
            last_bits = self._rreg(self.ControlReg) & 0x07
            if last_bits != 0:
                back_bits = (fifo_level - 1) * 8 + last_bits
            else:
                back_bits = fifo_level * 8

            for _ in range(fifo_level):
                back_data.append(self._rreg(self.FIFODataReg))
        else:
            status = self.MI_ERR

        return (status, back_data, back_bits)

    # -------- public ops ----------
    def request(self) -> tuple[int, int | None]:
        # REQA is 7 bits, so set BitFramingReg lower bits to 0x07
        self._wreg(self.BitFramingReg, 0x07)
        (status, back_data, back_bits) = self._to_card(self.PCD_TRANSCEIVE, [self.PICC_REQIDL])
        if status != self.MI_OK or back_bits != 0x10:
            return (self.MI_NOTAGERR, None)
        return (self.MI_OK, back_data[0] if back_data else 0)

    def anticoll(self) -> tuple[int, list[int] | None]:
        self._wreg(self.BitFramingReg, 0x00)
        (status, back_data, _) = self._to_card(self.PCD_TRANSCEIVE, [self.PICC_ANTICOLL, 0x20])
        if status != self.MI_OK or len(back_data) < 5:
            return (self.MI_ERR, None)

        uid = back_data[:5]
        # BCC check: XOR of first 4 bytes should equal 5th
        bcc = uid[0] ^ uid[1] ^ uid[2] ^ uid[3]
        if bcc != uid[4]:
            return (self.MI_ERR, None)

        return (self.MI_OK, uid[:4])


def lgpio_reset(rst_gpio: int, chip: int = 0):
    """Pulse RST low->high using lgpio."""
    h = lgpio.gpiochip_open(chip)
    try:
        lgpio.gpio_claim_output(h, rst_gpio, 1)
        lgpio.gpio_write(h, rst_gpio, 0)
        time.sleep(0.05)
        lgpio.gpio_write(h, rst_gpio, 1)
        time.sleep(0.05)
    finally:
        lgpio.gpiochip_close(h)


def main():
    RST_GPIO = 25           # BCM 25
    IGNORE_REPEAT_S = 1.5
    RESET_IDLE_S = 2.0
    POLL_DELAY = 0.05

    # Hard reset RC522 via lgpio
    lgpio_reset(RST_GPIO)

    r = RC522(spi_bus=0, spi_dev=0, spi_speed=200_000)
    r.init()

    last_uid = None
    last_uid_ts = 0.0
    last_any_ts = time.time()

    print("Scanning (lgpio+spidev). Present/remove tag anytime. Ctrl+C to stop.")

    try:
        while True:
            st, tag_type = r.request()
            if st == RC522.MI_OK:
                st2, uid = r.anticoll()
                if st2 == RC522.MI_OK and uid is not None:
                    now = time.time()
                    last_any_ts = now
                    uid_hex = ":".join(f"{b:02X}" for b in uid)

                    if not (uid_hex == last_uid and (now - last_uid_ts) < IGNORE_REPEAT_S):
                        print("UID:", uid_hex, "type:", hex(tag_type or 0))
                        last_uid = uid_hex
                        last_uid_ts = now

            # If reader gets “stuck”, re-init + reset
            if (time.time() - last_any_ts) > RESET_IDLE_S:
                r.antenna_off()
                r.close()
                lgpio_reset(RST_GPIO)
                r = RC522(spi_bus=0, spi_dev=0, spi_speed=200_000)
                r.init()
                last_any_ts = time.time()

            time.sleep(POLL_DELAY)

    except KeyboardInterrupt:
        pass
    finally:
        try:
            r.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
