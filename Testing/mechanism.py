from machine import Pin,PWM,UART,SPI
from time import *
import ustruct as struct
from math import *
from servo import Servo

'''



                                                                             
                                                 Gripper2_L----|          |----Gripper2_R
                                                               |          | 
                               Gripper1_L--\    /           \  | /     \  | /           \    /--Gripper1_R
                                            \__/             \__/       \__/             \__/
                                              \               /           \               /
                                               \             /             \             / 
                                                \           /               \           /
                                                 \_________/_________________\_________/
                                  servo_z_L _____|\ _____ /   / |       | \   \ _____ /|______servo_z_R
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
                                                M---Motor

Gripper1_R and Gripper2_L are at more height relative to other two.
'''

'this map function is use to map the values to desired scale'
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
####_map_#####        


'This class is designed for controlling servo motor for grippers'
class SCM:
    def __init__(self,pin,l_limit,u_limit,delay,cur_pos,req_pos,step_angle):        
        self.servo = Servo(pin)
        self.l_limit = l_limit
        self.u_limit = u_limit
        self.delay = delay
        self.cur_pos = cur_pos
        self.req_pos = req_pos
        self.step_angle = step_angle
    
    def set_to(self):#Servo
        while(self.cur_pos!=self.req_pos):
            if self.cur_pos<self.req_pos:
                self.cur_pos+=1
            else:
                self.cur_pos-=1
            print(self.servo,"Current angle:",self.cur_pos)
            self.servo.goto(int(_map_(self.cur_pos,0,180,0,1024)))
            sleep_ms(self.delay)
        if self.cur_pos==self.req_pos:
            print("Servo Done!!")
            
            
    def set_to_(self,obj):#Servo
        while(self.cur_pos!=self.req_pos or obj.cur_pos!=obj.req_pos):
            if self.cur_pos!=self.req_pos:
                if self.cur_pos<self.req_pos:
                    self.cur_pos+=1
                else:
                    self.cur_pos-=1
                print(self.servo,"Current angle:",self.cur_pos)
                self.servo.goto(int(_map_(self.cur_pos,0,180,0,1024)))
            if obj.cur_pos!=obj.req_pos:
                if obj.cur_pos<obj.req_pos:
                    obj.cur_pos+=1
                else:
                    obj.cur_pos-=1
                print(obj.servo,"Current angle:",obj.cur_pos)
                obj.servo.goto(int(_map_(obj.cur_pos,0,180,0,1024)))
            sleep_ms(self.delay)
        if self.cur_pos==self.req_pos and obj.cur_pos==obj.req_pos:
            print("Servo Done!!")
            
######__SCM__#######

##move_to_ function
#'THIS function is for controlling two Stepper motors simultaneously'
def move_to( step_pin1,dir_pin1,step_pin2,dir_pin2,position,cur_position):#stepper
        delay=100
        dir_pin1.value(1 if position > cur_position else 0)
        dir_pin2=dir_pin1
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
        
#####_move_to_####        

led=Pin(25,Pin.OUT)
led.on()
pin=Pin(28,Pin.OUT)
pin.off()
uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))
ps2=[0]*20



#grippers mechanism
gripper1_L=SCM(4,0,150,4,1,0,150) #'pin , l_limit , u_limit , delay , cur_pos , req_pos , step_angle'
gripper2_L=SCM(5,0,150,4,1,0,150)

gripper1_R=SCM(21,0,150,4,1,0,150)
gripper2_R=SCM(28,0,150,4,1,0,150)

#Pinouts for gripper extension mechanism servos(Crab mechanism
servo_z_R=SCM(3,0,100,20,0,100,180)
servo_z_L=SCM(2,0,100,20,0,100,180)


##Stepper pinouts 
step_z_L=Pin(18,Pin.OUT,value=0)
dir_z_L=Pin(19,Pin.OUT,value=0)

step_z_R=Pin(18,Pin.OUT,value=0)
dir_z_R=Pin(19,Pin.OUT,value=0)

req_pos_z=cur_pos_z=100000 #'Initial positions(a high number)'

steps_z_R=2500#'half of steps needed for grippers to go from bottom to top '

#'SHOOTING MECHANISM'

flag=[0]*20

shooter1=Servo(0)
shooter2=Servo(1)

##SHOOTING MECHANISM

lastTime=0

while True:
    if uart.any():

        try:
            message_bytes = uart.read()
            message = message_bytes.decode('utf-8')
            print("Uart conn")
            if message.find(',')!=-1:
                ps2 = list(map(int,message.split(",")))
        except (UnicodeError, ValueError) as e:
            print("Error decoding data:", e)
        
        
# BLDC_VESC_CODE
#         print("PS2 Value: ",ps2[1]-132+9)
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
## BLDC_VESC_CODE
        
        

        if(ps2[9] and flag[9]):
            req_pos_z=cur_pos_z+steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[9]=0
            lastTime=ticks_ms()

        if(ps2[11] and flag[11]):
            req_pos_z=cur_pos_z-steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)
            flag[11]=0
            lastTime=ticks_ms()
            

        if(ps2[7] and flag[7]==1):
            servo_z_R.req_pos=servo_z_R.cur_pos+servo_z_R.step_angle
            if servo_z_R.req_pos>servo_z_R.u_limit:
                servo_z_R.req_pos=servo_z_R.u_limit
            
            servo_z_L.req_pos=servo_z_L.cur_pos-servo_z_L.step_angle
            if servo_z_L.req_pos<servo_z_L.l_limit:
                servo_z_L.req_pos=servo_z_L.l_limit
            
            servo_z_L.set_to_(servo_z_R)
            flag[7]=0
            lastTime=ticks_ms()
        
        elif(ps2[4] and flag[4]==1):
            servo_z_R.req_pos=servo_z_R.cur_pos-servo_z_R.step_angle
            if servo_z_R.req_pos<servo_z_R.l_limit:
                servo_z_R.req_pos=servo_z_R.l_limit
            
            servo_z_L.req_pos=servo_z_L.cur_pos+servo_z_L.step_angle
            if servo_z_L.req_pos>servo_z_L.u_limit:
                servo_z_L.req_pos=servo_z_L.u_limit
            
            servo_z_L.set_to_(servo_z_R)
            flag[4]=0
            lastTime=ticks_ms()

        if(ps2[16] and flag[16]==1):

            gripper2_L.req_pos=gripper2_L.cur_pos+gripper2_L.u_limit
            if gripper2_L.req_pos>gripper2_L.u_limit:
                gripper2_L.req_pos=gripper2_L.u_limit
            
            
            gripper1_R.req_pos=gripper1_R.cur_pos+gripper1_R.u_limit
            if gripper1_R.req_pos>gripper1_R.u_limit:
                gripper1_R.req_pos=gripper1_R.u_limit

            gripper2_L.set_to_(gripper1_R)
            
            sleep_ms(1000)
            
            req_pos_z=cur_pos_z+steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)#step_pin,dir_pin,position,speed,cur_position            

            
            flag[16]=0
            lastTime=ticks_ms()
            print("Triangle")
            
        elif(ps2[17] and flag[17]==1):            
            
            gripper1_R.req_pos=gripper1_R.cur_pos+gripper1_R.u_limit
            if gripper1_R.req_pos>gripper1_R.u_limit:
                gripper1_R.req_pos=gripper1_R.u_limit
            
            gripper2_L.req_pos=gripper2_L.cur_pos+gripper2_L.u_limit
            if gripper2_L.req_pos>gripper2_L.u_limit:
                gripper2_L.req_pos=gripper2_L.u_limit
            gripper2_L.set_to_(gripper1_R)
            
            
            sleep_ms(1000)


            req_pos_z=cur_pos_z+steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)

            flag[17]=0
            lastTime=ticks_ms()
            print("Circle")
            
        
                
            
            

        
        
        
        if(ps2[18] and flag[18]==1):
            
            gripper1_L.req_pos=gripper1_L.cur_pos-gripper1_L.l_limit
            if gripper1_L.req_pos<gripper1_L.l_limit:
                gripper1_L.req_pos=gripper1_L.l_limit
            
            
            gripper2_R.req_pos=gripper2_R.cur_pos-gripper2_R.l_limit
            if gripper2_R.req_pos<gripper2_R.l_limit:
                gripper2_R.req_pos=gripper2_R.l_limit

            print( gripper2_L.req_pos,"		",gripper1_L.req_pos)
            
           
            
            
            req_pos_z=cur_pos_z-steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)#step_pin,dir_pin,position,speed,cur_position            

            sleep_ms(1000)
            gripper1_L.set_to_(gripper2_R)
            
            flag[18]=0
            lastTime=ticks_ms()
            print("Triangle")
            
            
            

        if(ps2[19] and flag[19]==1):
            
            gripper2_L.req_pos=gripper2_L.cur_pos-gripper2_L.l_limit
            if gripper2_L.req_pos<gripper2_L.l_limit:
                gripper2_L.req_pos=gripper2_L.l_limit
            
            
            gripper1_R.req_pos=gripper1_R.cur_pos-gripper1_R.l_limit
            if gripper1_R.req_pos<gripper1_R.l_limit:
                gripper1_R.req_pos=gripper1_R.l_limit

            
           
            
            
            req_pos_z=cur_pos_z-steps_z
            cur_pos_z=move_to(step_z_R,dir_z_R,step_z_L,dir_z_L,req_pos_z,cur_pos_z)#step_pin,dir_pin,position,speed,cur_position            

            sleep_ms(1000)
            gripper2_L.set_to_(gripper1_R)
            
            flag[19]=0
            lastTime=ticks_ms()
            
            
        if((ticks_ms()-lastTime)>=1000):
            for i in range(20):
                if (i!=12 and i!=10) and (i!=14 and i!=8):
                    flag[i]=1
            
        
        
        
#         print(lastTime)

