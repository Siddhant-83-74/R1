from machine import Pin,PWM,UART,SPI
from time import *
import ustruct as struct
from math import *
from servo_easing import Servo_easing
from servo import Servo


'''



                                                                             
                                                 Gripper1_L----|          |----Gripper2_R
                                                               |          | 
                               Gripper2_L--\    /           \  | /     \  | /           \    /--Gripper1_R
                                            \__/             \__/       \__/             \__/
                                              \               /           \               /
                                               \             /             \             / 
                                                \           /               \           /
                                                 \_________/_________________\_________/
                                 servo_crab_L _____|\ _____ /   / |       | \   \ _____ /|______servo_crab_R
                                                 | |  _  |   /  |  M1   |  \   |  _  | |
                                 stepper_L ______|_|_(_) |  /   |       |   \  | (_)_|_|______stepper_R 
                                                 | |_____| /    |_______|    \ |_____| |
                                                 |________/                   \________|                   
                                                 |                                     |
                                                 |                                     |
                                                 |                                     |  
                                                 |            _           _            |
                                                 |          /   \       /   \          |
                                                 |         | S1  |     | S2  |         |
                                                 |          \ _ /       \ _ /          |
                                                 |           | |         | |           |
                                                 |______     | |         | |     ______|
                                                 |      |    |R|         |R|    |      |       
                                                 |  M2  |    | |         | |    |  M3  |
                                                 |      |    | |         | |    |      |
                                                 |______|____|_|_________|_|____|______|
                                             
                                                S---Shooter
                                                R---Roller
  
  Grippers range 60-180(open at 180 and close at 60)
  the crab arm will come down at 10 and go back at 180
'''



led = Pin(25, Pin.OUT)
led.on()

def move_to( step_pin1,dir_pin1,step_pin2,dir_pin2,position,cur_position):#stepper
        delay=90
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
def move_to_( step_pin1,dir_pin1,position,cur_position):#stepper
        delay=90
        if position > cur_position:
           val =1
        elif position < cur_position:
            val=0
        dir_pin1.value(val)
        while cur_position != position:
                step_pin1.value(1)
                sleep_us(delay)
                step_pin1.value(0)
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

g_servo_r_pin1= 6#right gripper of both sides is pin1
g_servo_r_pin2= 7

g_servo_l_pin1= 10
g_servo_l_pin2= 11

gripper_1L=Servo_easing(10,50,180,179,180,1000)#         pin,l_limit,u_limit,start_angle,end_angle,duration
gripper_2L=Servo_easing(11,50,180,179,180,1000)

gripper_1R=Servo_easing(6,50,180,179,180,1000)
gripper_2R=Servo_easing(7,50,180,179,180,1000)

servo_crab_L=Servo_easing(5,13,151,151,13,3000)
servo_crab_R=Servo_easing(4,14,175,175,14,3000)

# sleep_ms(1000)
servo_crab_L.linear_move(servo_crab_R)

gripper_1L.ease_in_out_expo_move(gripper_1R)
gripper_2R.ease_in_out_expo_move(gripper_2L)


# servo_r.goto(39, 0.01)
# servo_l.goto(39, 0.01)

step_z_L=Pin(18,Pin.OUT,value=0)
dir_z_L=Pin(19,Pin.OUT,value=0)

step_z_R=Pin(20,Pin.OUT,value=0)
dir_z_R=Pin(21,Pin.OUT,value=0)


req_pos_z=cur_pos_z=100000 #'Initial positions(a high number)'

steps_z=2500
cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L, 100250,cur_pos_z)
cur_pos_zl=100250
cur_pos_zl=move_to_(step_z_L,dir_z_L,100600,cur_pos_zl)

uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))
ps2=[0]*20

flag=[0]*20

lastTime=0

f = 0##??

shooter1=Servo(14)
shooter2=Servo(15)

flag_grippers=1

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
            val = -(ps2[3]-132+9)
            print("Joystick value : ",val)
            value = int(_map_(val,-100,9,88,175))# 0.332-0.342V,,156--1186
            print("bldc value: ",value)
            shooter1.goto(round(_map_(175,0,180,0,1024)))
            shooter2.goto(round(_map_(175,0,180,0,1024)))
            flag[14]=0
            
        if(ps2[12]):
            shooter1.goto(round(_map_(0,0,180,0,1024)))
            shooter2.goto(round(_map_(0,0,180,0,1024)))
            flag[12]=0
            flag[14]=0
            flag[8]=0
            flag[10]=0
            print("12 pressed")
            
        if(ps2[10]):
            flag[10]=1
            print("down")
            
        if(flag[10]==1):   
            shooter1.goto(round(_map_(0,0,180,0,1024)))
            shooter2.goto(round(_map_(0,0,180,0,1024)))
            flag[12]=0
            flag[14]=0
            flag[8]=0
            flag[10]=0
            lastTime=ticks_ms()
            print("up")
            
        if(ps2[8]):
            flag[8]=1
            print("downn")
            
        if(flag[8]==1):
            sleep_ms(250)
            shooter1.goto(round(_map_(175,0,180,0,1024)))
            shooter2.goto(round(_map_(175,0,180,0,1024)))
            flag[8]=0
            lastTime=ticks_ms()
            print("down")
            
        if ps2[7] and flag[7] and flag_grippers==1:
            print("Servo_L_G")

            gripper_1R.set_angle180_0()
            gripper_2R.set_angle180_0()
            gripper_1L.set_angle180_0()
            gripper_2L.set_angle180_0()
            
            servo_crab_L.set_angle0_180()
            servo_crab_R.set_angle0_180()
            
            
            gripper_1R.ease_in_out_expo_move(gripper_1L)
            gripper_2R.ease_in_out_expo_move(gripper_2L)
            
            #sleep_ms(50)

            servo_crab_L.ease_in_out_expo_move(servo_crab_R)
            

            
            flag[4] = 0
            lastTime = ticks_ms()
            flag_grippers=0
            
        if ps2[4] and flag[4] and flag_grippers==0:
            print("Servo_R_G")
            gripper_1R.set_angle0_180()
            gripper_2R.set_angle0_180()
            gripper_1L.set_angle0_180()
            gripper_2L.set_angle0_180()
            
            servo_crab_L.set_angle180_0()
            servo_crab_R.set_angle180_0()
            
            servo_crab_L.ease_in_out_expo_move(servo_crab_R)
            #sleep_ms(50)
            gripper_1R.ease_in_out_expo_move(gripper_1L)
            gripper_2R.ease_in_out_expo_move(gripper_2L)
            flag[7] = 0
            lastTime = ticks_ms()
            flag_grippers=1
            
        if ps2[16] and flag[16] and flag_grippers==1:
            
            print("Stepper Down")
            req_pos_z=cur_pos_z-2200
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            print("Upper Grippers Open")
            gripper_1R.set_angle0_180()
            gripper_1L.set_angle0_180()
            gripper_1L.ease_in_out_expo_move(gripper_1R)
#             g_servo_r1.goto(1024, 0.01)
#             g_servo_l1.goto(1024, 0.01)
            
            flag[16] = 0
            lastTime=ticks_ms()
            
        if ps2[18] ==1 and flag[18] ==1 and flag_grippers==1:
            print("Upper Grippers Close")
#             g_servo_r1.goto(280, 0.01)
#             g_servo_l1.goto(280, 0.01)
            gripper_1R.set_angle180_0()
            gripper_1L.set_angle180_0()
            gripper_1L.ease_in_out_expo_move(gripper_1R)
            sleep_ms(500)
            print("Stepper Up")
            req_pos_z=cur_pos_z+2200
            move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[18] = 0
            lastTime=ticks_ms()
       
        if ps2[19] ==1 and flag[19] ==1 and flag_grippers==1:
            print("Lower Grippers Close")
            gripper_2R.set_angle180_0()
            gripper_2L.set_angle180_0()
            gripper_2L.ease_in_out_expo_move(gripper_2R)
#             g_servo_r2.goto(280, 0.01)
#             g_servo_l2.goto(280, 0.01)
            sleep_ms(500)
            print("Stepper Up")
            req_pos_z=cur_pos_z+2000
            move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[19] = 0
            lastTime=ticks_ms()

        if ps2[17] and flag[17] and flag_grippers==1:
            print("Stepper Down")
            req_pos_z=cur_pos_z-2000
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            print("Lower Grippers Open")
            gripper_2R.set_angle0_180()
            gripper_2L.set_angle0_180()
            gripper_2L.ease_in_out_expo_move(gripper_2R)
            flag[17] = 0
            lastTime=ticks_ms()
            
        if((ticks_ms()-lastTime)>=1000):
            for i in range(20):
                if (i!=12 and i!=10) and (i!=14 and i!=8):
                    flag[i]=1



 


