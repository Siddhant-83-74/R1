from machine import Pin,PWM,UART,SPI
from time import *
import ustruct as struct
from math import *
from servoe import Servo
from servo import Servo

def move_to( step_pin1,dir_pin1,step_pin2,dir_pin2,position,cur_position):#stepper
        delay=100
        if position > cur_position:
           val =1
        elif position < cur_position:
            val=0
        dir_pin1.value(val)
        dir_pin2.value(val)
        while cur_position != position:
                step_pin1.value(1)
                step_pin2.value(1)
                sleep_us(delay)
                step_pin1.value(0)
                step_pin2.value(0)
                sleep_us(delay)
                cur_position += 1 if position >cur_position else -1

        print(cur_position)
        return cur_position

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
        
pin1 = 4
pin2 = 5

g_servo_r_pin1= 6
g_servo_r_pin2= 7

g_servo_l_pin1= 10
g_servo_l_pin2= 11

g_servo_r1 = Servo(g_servo_r_pin1)
g_servo_r2 = Servo(g_servo_r_pin2)

g_servo_l1 = Servo(g_servo_l_pin1)
g_servo_l2 = Servo(g_servo_l_pin2)

servo_r = Servo(pin1)
servo_l = Servo(pin2)

start_pos= 0
deg = (start_pos*1024)/180

deg_g = (180*1024)/180

g_servo_r1.goto(deg_g)
g_servo_r2.goto(deg_g)
g_servo_l1.goto(deg_g) 
g_servo_l2.goto(deg_g)

servo_r.goto(39)
servo_l.goto(39)

step_z_L=Pin(18,Pin.OUT,value=0)
dir_z_L=Pin(19,Pin.OUT,value=0)

step_z_R=Pin(20,Pin.OUT,value=0)
dir_z_R=Pin(21,Pin.OUT,value=0)

req_pos_z=cur_pos_z=100000 #'Initial positions(a high number)'

steps_z=2500

uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))
ps2=[0]*20

flag=[0]*20

lastTime=0

f = 0

shooter1=Servo(14)
shooter2=Servo(15)

while True:
    if uart.any():

        try:
            message_bytes = uart.read()
            message = message_bytes.decode('utf-8')
            #print("Uart conn")
            if message.find(',')!=-1:
                ps2 = list(map(int,message.split(",")))
#                 print(ps2)
        except (UnicodeError, ValueError) as e:
            print("Error decoding data:", e)
        
        if(ps2[14]):
            shooter1.goto(round(_map_(88,0,180,0,1024)))
            shooter2.goto(round(_map_(88,0,180,0,1024)))
            flag[14]=1
            flag[8]=0
            flag[10]=0
            sleep_ms(100)
            print("14 pressed")
            
        if(flag[14]==1):
            val = -(ps2[3]-132)
            value = int(_map_(val,-100,9,88,156))# 0.332-0.342V
            print("value: ",value)
            shooter1.goto(round(_map_(value,0,180,0,1024)))
            shooter2.goto(round(_map_(value,0,180,0,1024)))
            
        if(ps2[12]):
            shooter1.goto(round(_map_(0,0,180,0,1024)))
            shooter2.goto(round(_map_(0,0,180,0,1024)))
            flag[12]=0
            flag[14]=0
            flag[8]=0
            flag[10]=0
            print("12 pressed")
            
        if(ps2[8]):
            flag[8]=1
            print("upp")
            
        if(flag[8]==1):    
            shooter1.goto(round(_map_(156,0,180,0,1024)))
            shooter2.goto(round(_map_(156,0,180,0,1024)))
#             flag[8]=0
            lastTime=ticks_ms()
            print("up")
            
        if(ps2[10]):
            flag[10]=1
            print("downn")
            
        if(flag[10]==1):    
            shooter1.goto(round(_map_(150,0,180,0,1024)))
            shooter2.goto(round(_map_(150,0,180,0,1024)))
#             flag[8]=0
            lastTime=ticks_ms()
            print("down")
            
        if ps2[4] and flag[4]:
            print("Servo_L_G")
            deg = (0*1024)/180
            servo_r.goto(deg)
            servo_l.goto(deg)
            flag[4] = 0
            lastTime=ticks_ms()
            
        if ps2[7] and flag[7]:
            print("Servo_R_G")
            deg = (180*1024)/180
            servo_r.goto(deg)
            servo_l.goto(deg)
            flag[7] = 0
            lastTime=ticks_ms()
      
        if ps2[16] and flag[16]:
            
            print("Stepper Down")
            req_pos_z=cur_pos_z-steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            print("Upper Grippers Open")
            g_servo_r1.goto(1024)
            g_servo_l1.goto(1024)
            flag[16] = 0
            lastTime=ticks_ms()
            
        if ps2[18] ==1 and flag[18] ==1:
            print("Upper Grippers Close")
            g_servo_r1.goto(400)
            g_servo_l1.goto(400)
            sleep_ms(500)
            print("Stepper Up")
            req_pos_z=cur_pos_z+2500
            move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[18] = 0
            lastTime=ticks_ms()
       
        if ps2[19] ==1 and flag[19] ==1 :
            print("Lower Grippers Close")
            g_servo_r2.goto(400)
            g_servo_l2.goto(400)
            sleep_ms(500)
            print("Stepper Up")
            req_pos_z=cur_pos_z+2000
            move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[19] = 0
            lastTime=ticks_ms()

        if ps2[17] and flag[17]:
            print("Stepper Down")
            req_pos_z=cur_pos_z-2000
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            print("Lower Grippers Open")
            g_servo_r2.goto(1024)
            g_servo_l2.goto(1024)
            flag[17] = 0
            lastTime=ticks_ms()
            
        if((ticks_ms()-lastTime)>=1000):
            for i in range(20):
                if (i!=12 and i!=10) and (i!=14 and i!=8):
                    flag[i]=1
