from machine import Pin, UART, PWM, SPI, I2C
from time import *
import ustruct as struct
from nrf24l01 import *
from micropython import const
import math

# from servo import Servo
led = Pin(25, Pin.OUT)
led.on()

# UART
uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

# DRIVE
max_pwm = 115

m1_pwm = PWM(Pin(5))
m1_in1 = Pin(4, Pin.OUT, value=0)

m2_pwm = PWM(Pin(6))
m2_in1 = Pin(7, Pin.OUT, value=0)

m3_pwm = PWM(Pin(3))
m3_in1 = Pin(2, Pin.OUT, value=0)

roller_pwm = PWM(Pin(1))
roller_dir = Pin(0, Pin.OUT)
roller_dir.on()

roller_pwm.freq(9000)
roller_pwm.duty_u16(0 * 257)

# DRIVE
ps2 = [0] * 20

def _map_(val, loval, hival, tolow, tohigh):
    if val < loval:
        val = loval
    elif val > hival:
        val = hival
    if loval <= val <= hival:
        return (val - loval) / (hival - loval) * (tohigh - tolow) + tolow
    else:
        raise ValueError

def drivepwm(speed, in_1, pwm_pin):
    pwm = pwm_pin
    pwm.freq(9000)
    dir = in_1
    dir.freq(1250)
    if speed < 0:
        in_1.duty_u16(65530)
        pwm.duty_u16(-1 * speed)
    elif speed > 0:
        in_1.duty_u16(10500)
        pwm.duty_u16(speed)
    else:
        pwm.duty_u16(0)

def drive(speed, in_1, pwm_pin):
    pwm = pwm_pin
    pwm.freq(9000)
    if speed < 0:
        in_1.off()
        pwm.duty_u16(-1 * speed)
    elif speed > 0:
        in_1.on()
        pwm.duty_u16(speed)
    else:
        pwm.duty_u16(0)

def i_k(x, y, w, z):
    if w != 0 and w>0:
        s1 = 30
        s2 = 30
        s3 = 30
    elif z != 0 and z<0:
        s1 = 59
        s2 = 59
        s3 = 59
    elif w != 0 and w<0:
        s1 = -30
        s2 = -30
        s3 = -30
    elif z != 0 and z>0:
        s1 = -59
        s2 = -59
        s3 = -59
    else:
         s1=int(1*x)
         s2=int(-0.508*x-0.88*y)
         s3=int(-0.5045*x+0.8725*y)
        
    s1 = int(_map_(s1, -137, 137, -max_pwm, max_pwm) * 257)
    s2 = int(_map_(s2, -137, 137, -max_pwm, max_pwm) * 257)
    s3 = int(_map_(s3, -137, 137, -max_pwm*1, max_pwm*1) * 257)
    
#     print("s1: ", s1)
#     print("s2: ", s2)
#     print("s3: ", s3)
    
    
    drive(s1, m1_in1, m1_pwm)
    drive(s2, m2_in1, m2_pwm)
    drive(s3, m3_in1, m3_pwm)

pipe = (b"\x53\x49\x44\x4D\x41")  # 'SIDMA' on the arduino
spi = SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12))
cfg = {"spi": 1, "miso": 12, "mosi": 15, "sck": 14, "csn": 13, "ce": 11}
csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)

# Initializing NRF
nrf = NRF24L01(spi, csn, ce, channel=100, payload_size=20)
nrf.open_rx_pipe(0, pipe)
nrf.set_power_speed(POWER_1, SPEED_2M)  # power1 = -12 dBm, speed_2m = 2 mbps
nrf.start_listening()
print('readSensorLoop, waiting for packets... (ctrl-C to stop)')

flag = 0
flag1 = 0
flag_8=0
lastTime = 0

while True:
    if nrf.any():
        while nrf.any():
            buf = nrf.recv()
            ps2 = struct.unpack(">20B", buf)
            print(ps2)
            try:
                message = ','.join(map(str, ps2))
                uart.write(message.encode('utf-8'))
                utime.sleep_ms(7)
            except:
                print("UART error")
            x = int(_map_(ps2[0], 0, 255, 100, -100))
            y = int(_map_(ps2[1], 0, 255, 100, -100))
            w = int(_map_(ps2[2], 0, 255, max_pwm * 0.4, -max_pwm * 0.4))
            z = int(_map_(ps2[3], 0, 255, max_pwm * 0.635, -max_pwm * 0.635))
#             print(x - 3)
#             print(y - 3)
#             print(w - 1)
#             print(z -2)
            i_k(x - 3, y - 3, w - 1, z-2)
            
            if ps2[15] and flag == 1:
                print("roller on")
                roller_pwm.duty_u16(255 * 257)
                flag = 0
                lastTime = ticks_ms()
            elif ps2[13] and flag1 == 1:
                print("roller off")
                roller_pwm.duty_u16(0)
                flag1 = 0
                lastTime = ticks_ms()
                
            if(ps2[8] and flag_8==1):
                print("roller off")
                roller_dir.off()
                roller_pwm.duty_u16(255 * 257)
                sleep_ms(95)
                roller_dir.on()
                roller_pwm.duty_u16(255 * 257)
                flag_8==0

            
    #             flag[8]=0
                lastTime=ticks_ms()
                print("down")
            
                
            if ps2[11] == 1:
                drive(12000, m1_in1, m1_pwm)
                drive(-6405, m2_in1, m2_pwm)
                drive(-6405, m3_in1, m3_pwm)
                
            if ps2[9] == 1:
                drive(-12000, m1_in1, m1_pwm)
                drive(6405, m2_in1, m2_pwm)
                drive(6405, m3_in1, m3_pwm)
                
            if ticks_ms() - lastTime >= 1000:
                flag1 = 1
                flag = 1
                flag_8=1





