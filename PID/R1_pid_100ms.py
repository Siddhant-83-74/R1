from machine import *
from time import sleep,sleep_ms,ticks_ms
import ustruct as struct
from nrf24l01 import *
from math import *
ps2=[0]*20
max_rpm=250
led=Pin(25,Pin.OUT)
#led.on()
def _map_(val, loval, hival, tolow, tohigh):
         if val<loval:
                 val=loval
         elif val>hival:
             val=hival
         if loval <= val <= hival:
             res=(val - loval)/(hival-loval)*(tohigh-tolow) + tolow
             return (val - loval)/(hival-loval)*(tohigh-tolow) + tolow
         else:
             raise(ValueError)
            
            
class Encoder_:
    pin_A:Pin
    pin_B:Pin
# Constants for the encoder pins
    def __init__(self,a,b,pwm,dir_):
        self.PIN_A = a
        self.PIN_B = b
        self.s_map=0
    # Initialize2variables to keep track of encoder state and count
        self.count = 0
        self.last_A = 0
        self.last_B = 0
        self.state = 0
        #rpm=0# To keep track of encoder state for determining direction
        self.ppr=650

        self.error=self.last_Time=self.lastErr=self.eInt=self.eDer=0
        self.Kp=0
        self.Ki=0
        self.Kd=0
        self.rpmSp=0
        # rpmSp*=2
        self.rpmAcl=0

        self.lastTime=0
        self._speed=0

        self._pwm=PWM(Pin(pwm))
        self._dir=Pin(dir_,Pin.OUT,value=0)

    def rpm_(self,count):
        self.rpmAcl=(self.count/self.ppr)*600
        
    # Callback function for the A signal interrupt
    def _map_(val, loval, hival, tolow, tohigh):
         if val<loval:
                 val=loval
         elif val>hival:
             val=hival
         if loval <= val <= hival:
             res=(val - loval)/(hival-loval)*(tohigh-tolow) + tolow
             return (val - loval)/(hival-loval)*(tohigh-tolow) + tolow
         else:
             raise(ValueError)
            
    def drive(self):
            self._pwm.freq(1000)
            self._speed=int(self._speed)
    #         print("SPEED: ",speed)
            if self._speed<0:
                self._dir.off()
    #             in_2.on()
                self._pwm.duty_u16(-1*self._speed)
                #print("drive1")
                
            elif self._speed>0:
                # print("drive1el")
                 self._dir.on()
    #              in_2.off()
                 self._pwm.duty_u16(self._speed)
            else:
                 self._pwm.duty_u16(0)
    def drive_(self,speed):
            self._pwm.freq(1000)
            _speed_=speed
    #         print("SPEED: ",speed)    
            self._pwm.duty_u16(speed)
    # #             in_2.on()
    def on_encoder_A_irq(self,pin):
    #     global count, last_A, last_B
        current_A = self.pin_A.value()
        current_B = self.pin_B.value()

        if current_A != self.last_A:
            if current_A == current_B:
                self.count+=1
            else:
                self.count-=1
        self.last_A = current_A

    def pid(self):
    #     global rpmAcl,rpmSp,last_Time,lastErr,eInt,_speed
        
        time=(ticks_ms()-self.last_Time)/1000.0
        self.error=self.rpmSp-self.rpmAcl
        self.eDer=(self.error-self.lastErr)/time
        self.eInt=self.eInt+self.error*time
#         print(self.Kp)
        self._speed=self.Kp*self.error+self.Ki*self.eInt+self.Kd*self.eDer

        self.last_Time=time
        self.lastErr=self.error

        
    def setup(self):
        # Initialize the GPIO pins for the encoder signals
        self.pin_A = Pin(self.PIN_A, Pin.IN)
        self.pin_B = Pin(self.PIN_B, Pin.IN)

        # Attach interrupt handler to pin A
        self.pin_A.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.on_encoder_A_irq)


def i_k(x,y,w):
     #print(x," ",y)
    x=int(_map_(x,-100,100,-200,200))
    y=int(_map_(y,-100,100,-200,200))
    w=int(_map_(w,-100,100,-200,200))
     
    m1.s_map=(-2/3.0*x+w)
    m2.s_map=(1/3.0*x-1/sqrt(3)*y+w)
    m3.s_map=(1/3.0*x+1/sqrt(3)*y+w)
     
    

     
    m1.rpmSp = _map_(m1.s_map, -250, 250, -max_rpm, max_rpm)
    m2.rpmSp= _map_(m2.s_map, -250, 250, -max_rpm, max_rpm)
    m3.rpmSp = _map_(m3.s_map, -250, 250, -max_rpm, max_rpm)
#NRF_'s attributes 
pipe = (b"\x53\x49\x44\x4D\x41") # 'SIDMA' on the arduino
spi = SPI(1, sck=Pin(14), mosi=Pin(15), miso=Pin(12))
cfg = {"spi": 1, "miso": 12, "mosi": 15, "sck": 14, "csn": 13, "ce": 11} 
csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)     
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)

#Initializing NRF
nrf = NRF24L01(spi, csn, ce, channel = 100, payload_size=20)
nrf.open_rx_pipe(0,pipe)
nrf.set_power_speed(POWER_1, SPEED_2M) # power1 = -12 dBm, speed_2m = 2 mbps
nrf.start_listening()
print('readSensorLoop, waiting for packets... (ctrl-C to stop)')
####

flag=0



m1=Encoder_(22,26,5,4)#a,b,pwm,dir_
m2=Encoder_(20,21,10,6)
m3=Encoder_(18,19,2,7)


m1.setup()
m2.setup()
m3.setup()

m1.Kp=30
m1.Ki=0.15 #at 16.6 V
m1.Kd=20

m2.Kp=30
m2.Ki=0.1 #at 16.6 V
m2.Kd=20

m3.Kp=20
m3.Ki=0.1 #at 16.6 V
m3.Kd=20

m1.rpmSp=0
m2.rpmSp=0
m3.rpmSp=0

# m1.Kp=m2.Kp=m3.Kp=50
# m1.Ki=m2.Ki=m3.Ki=0.5
# m1.Kd=m2.Kd=m3.Kd=36
lastTime=0
while True:
    if nrf.any(): 
        while nrf.any():
            if(ticks_ms()-lastTime>=100):
                if flag==0:## this if block deals with cytron input error
                        m1.drive_(0)
                        m2.drive_(0)
                        m3.drive_(0)
                        sleep(1)
                        flag=1
    #             print("NRF")
                buf= nrf.recv()
                ps2= struct.unpack(">20B", buf)
                led.on()
                
                x=int(_map_(ps2[2],0,255,-100,100))
                y=int(_map_(ps2[3],0,255,-100,100))
                w=int(_map_(ps2[0],0,255,100,-100))
                x-=3
                y+=3
                w+=3
                if x==0 and y==0 and w==0:
                    m1.drive_(0)
                    m2.drive_(0)
                    m3.drive_(0)
#                 print(x,"  ",y,"  ",w)
                
#                 print(y)
#                 m1.rpmSp=round(_map_(x,-100,100,250,-250))
#                 m2.rpmSp=round(_map_(y,-100,100,250,-250))
#                 m3.rpmSp=round(_map_(w,-100,100,250,-250))
                i_k(x,y,w)
                
                 
                if flag==0:
                        m1.drive1(0)
                        m2.drive1(0)
                        m3.drive1(0)
                        sleep(1)
                        flag=1
                m1.rpm_(m1.count)
                m2.rpm_(m2.count)
                m3.rpm_(m3.count)

                m1.pid()
                m2.pid()
                m3.pid()
                
                m1.drive()
                m2.drive()
                m3.drive()
        #        print()
                print("	Set Point m1",m1.rpmSp," Set Pointm2",m2.rpmSp," Set Pointm3",m3.rpmSp,"	RPM M1: ",m1.rpmAcl," RPM M2: ",m2.rpmAcl," RPM M3: ",m3.rpmAcl)
        #         print("RPM M2: ",m2.rpmAcl)
        #         print("RPM M3: ",m2.rpmAcl)
        #         print()
        #         print("RPM set point: ",rpmSp)

                m1.rpm=0
                m2.rpm=0
                m3.rpm=0
                
                m1.count=0
                m2.count=0
                m3.count=0
                
                lastTime=ticks_ms()
           

        
            
            











