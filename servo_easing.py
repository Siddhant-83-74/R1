
from machine import *
from time import sleep,sleep_ms,ticks_ms,ticks_us
from servo import Servo
import math
def _map_(val, loval, hival, tolow, tohigh): 
     if val<loval:
             val=lovals
     elif val>hival:
             val=hival
     if loval <= val <= hival:
         res=(val - loval)/(hival-loval)*(tohigh-tolow) + tolow
         return (val - loval)/(hival-loval)*(tohigh-tolow) + tolow
     else:
         raise(ValueError)
####
class Servo_easing:
    
    def __init__(self,pin,l_limit,u_limit,start_angle,end_angle,duration):        
        self.servo = Servo(pin)
        self.l_limit = l_limit
        self.u_limit = u_limit
#         self.delay = delay
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.duration = duration
        self.cur_pos=start_angle-1
        self.req_pos=start_angle+1
        
    
    def set_angle0_180(self):#f
        self.start_angle=self.l_limit
        self.end_angle=self.u_limit
        
    def set_angle180_0(self):
        self.start_angle=self.u_limit
        self.end_angle=self.l_limit
        
    def set_to(self):#Servo
            while(self.cur_pos!=self.req_pos):
                if self.cur_pos<self.req_pos:
                    self.cur_pos+=1
                else:
                    self.cur_pos-=1
                print(self.servo,"Current angle:",self.cur_pos)
                self.servo.goto(int(_map_(self.cur_pos,0,180,0,1024)))
#                 sleep_ms(self.delay)
#             if self.cur_pos==self.req_pos:
#                 print("Servo Done!!")
            
            
    def set_to_(self,obj):#Servo
        while(self.cur_pos!=self.req_pos or obj.cur_pos!=obj.req_pos):
#             print(self.cur_pos,"		",self.req_pos)            
            if self.cur_pos!=self.req_pos:
                if self.cur_pos<self.req_pos:
                    self.cur_pos+=1
                else:
                    self.cur_pos-=1
                print("Object 1")
                self.servo.goto(int(_map_(self.cur_pos,0,180,0,1024)))
#             print(obj.cur_pos,"		",obj.req_pos)
            if obj.cur_pos!=obj.req_pos:
                if obj.cur_pos<obj.req_pos:
                    obj.cur_pos+=1
                else:
                    obj.cur_pos-=1
                print("Object 2")
                obj.servo.goto(int(_map_(obj.cur_pos,0,180,0,1024)))
#             sleep_ms(self.delay)
#         if self.cur_pos==self.req_pos and obj.cur_pos==obj.req_pos:
#             print("")            
            
    def ease_out_expo(self,cur_time):#Give this function time in milliseconds it will give you 
        time=(_map_(cur_time,0,self.duration,0,1))
        cur_value=1-math.pow(2,-10*time)
        cur_angle=int(_map_(cur_value,0,1,self.start_angle,self.end_angle))
        return cur_angle
        
    def ease_out_expo_move(self,obj=None):
        if obj is None:
            print("if case")
            start_time=ticks_ms()
            while(ticks_ms()-start_time<=self.duration):
                self.req_pos=self.ease_out_expo(ticks_ms()-start_time)
                self.set_to()
                print(self.req_pos)
            self.start_angle=self.end_angle
        else:
            print("Else Case")
            start_time=ticks_ms()
            while(ticks_ms()-start_time<=self.duration):
                self.req_pos=self.ease_out_expo(ticks_ms()-start_time)
                self.set_to_(obj)
                print(self.req_pos)
            self.start_angle=self.end_angle
            obj.start_angle=obj.end_angle
            
            
            
    def ease_in_out_expo(self,cur_time):#Give this function time in milliseconds it will give you 
        time=(_map_(cur_time,0,self.duration,0,1))
        if time == 0:
            cur_value = 0
        elif time == 1:
            cur_value = 1
        elif time < 0.5:
            cur_value = math.pow(2, 20 * time - 10) / 2
        else:
            cur_value = (2 - math.pow(2, -20 * time + 10)) / 2

        cur_angle=int(_map_(cur_value,0,1,self.start_angle,self.end_angle))
        return cur_angle
        
    def ease_in_out_expo_move(self,obj=None):
        if obj is None:
            print("if case")
            start_time=ticks_ms()
            while(ticks_ms()-start_time<=self.duration):
                self.req_pos=self.ease_in_out_expo(ticks_ms()-start_time)
                self.set_to()
                print(self.req_pos)
            self.start_angle=self.end_angle
        else:
            print("Else case")
            start_time=ticks_ms()
            while(ticks_ms()-start_time<=self.duration):
                self.req_pos=self.ease_in_out_expo(ticks_ms()-start_time)
                obj.req_pos=self.req_pos
                self.set_to_(obj)
                print("Else case	",self.req_pos)
            self.start_angle=self.end_angle
            obj.start_angle=obj.end_angle
            
    def linear(self,cur_time):#Give this function time in milliseconds it will give you 
            time=(_map_(cur_time,0,self.duration,0,1))
            cur_value=time
            cur_angle=int(_map_(cur_value,0,1,self.start_angle,self.end_angle))
            return cur_angle
            
    def linear_move(self,obj=None):
            if obj is None:
                print("if case")
                start_time=ticks_ms()
                while(ticks_ms()-start_time<=self.duration):
                    self.req_pos=self.linear(ticks_ms()-start_time)
                    self.set_to()
                    print(self.req_pos)
                    self.start_angle=self.end_angle
            else:
                print("Else case")
                start_time=ticks_ms()
                while(ticks_ms()-start_time<=self.duration):
                    self.req_pos=self.linear(ticks_ms()-start_time)
                    obj.req_pos=self.req_pos
                    self.set_to_(obj)
                    print("Else case	",self.req_pos)
                self.start_angle=self.end_angle
                obj.start_angle=obj.end_angle            
        
        
        
    
        
       
            
            




    








