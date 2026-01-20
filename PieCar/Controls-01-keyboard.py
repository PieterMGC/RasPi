from gpiozero import Motor, Servo
from time import sleep
from gpiozero.pins.lgpio import LGPIOFactory
import pygame

factory = LGPIOFactory()

motor = Motor(forward=27, backward=17, enable=18, pwm=True, pin_factory=factory)
servo = Servo(4, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

def main():
    print("Program started! Stop by closing the window or pressing Ctrl+C")

    pygame.init()
    screen = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Arrow Key Controller")
    clock = pygame.time.Clock()

    try:
        while True:
            # Handle quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            keys = pygame.key.get_pressed()

            # ---- DRIVE ----
            if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
                motor.forward()
            elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
                motor.backward()
            else:
                motor.stop()

            # ---- STEER ----
            if keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
                servo.max()
            elif keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                servo.min()
            else:
                servo.mid()

            clock.tick(60)  # 60 updates per second

    except KeyboardInterrupt:
        motor.stop()
        sleep(0.2)
        servo.value = None
        sleep(0.2)
        pygame.quit()
        print("Program stopped!")

if __name__ == "__main__":
    main()