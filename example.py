import cv2
import time
import serial
from gaze_tracking import GazeTracking
# from gpiozero import LED
gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
startTime = time.time()
s=time.time()
startCommandTime = time.time()
#total blink number
countblink=0
state = 0    # 
lookingState = 0 # 1=> Basic Command (looking right) 2=> special command (looking left)
#True when eye is close
eyeClose=False
#True when eye is open
eyeOpen=True
#when true increment blinkcounter 
conterFlag=False
blinkStartTime = time.time() 
import pygame
path = "/home/pi/Desktop/direction/" 
sound_files = ["right.wav","left.wav","forward.wav","backward.wav","stop.wav","close.wav"]  
num_files=["one.wav","two.wav","three.wav","four.wav"]
pygame.mixer.init()
speaker_volume = 1
i=0 #to reach audio array elements
framCounter =0 
modFlag=False
backFlag = False
rightLeft = False

if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyACM0',9600, timeout=1)
    ser.flush()      
    try:
        while True: 
            
            #take the current time with every frame
            curentTime = time.time()    
            # We get a new frame from the webcam
            success, frame = webcam.read()            
            
            #print(success)
            # We send this frame to GazeTracking to analyze it
            gaze.refresh(frame)
            frame = gaze.annotated_frame()
            text = ""
            # framCounter+=1
            # print(framCounter,curentTime)
            difference = curentTime - blinkStartTime 
            # ratio= gaze.is_blinking()
            # print(ratio)

            if (gaze.is_blinking()==1): 
                print("close")
                pygame.mixer.music.load("/home/pi/Desktop/direction/close.wav")
                pygame.mixer.music.play()
                eyeOpen=False
                if not eyeClose:
                    blinkStartTime = time.time() 
                    eyeClose = True
                if(((difference<= 3) and (difference>= 2) )  and eyeClose):
                    modFlag=True
  

            elif(gaze.is_blinking()==2): 
                print("open")
                eyeOpen=True
                eyeClose =False
                if(modFlag):
                    if(not conterFlag):
                        countblink +=1
                        pygame.mixer.music.load(path + num_files[i])
                        pygame.mixer.music.play()
                        i=i+1
                        blinkStartTime = time.time()
                    modFlag=False
               
            if(countblink==2 and lookingState==0):
                #print("current time=",curentTime)
                #print("start time=",s)
                if(state != 3):
                    s=time.time()
                    #print("start time=",s)
                    state=3
                    print("when we talk strt ")
                if(curentTime-s >= 2):
                    lookingState=1
                    print("looking state = ",lookingState)
                #conterFlag=True
            if(countblink==3 and (lookingState==0 or lookingState==1 )):
                    print("enter state4")
                    conterFlag=True
                    lookingState=2
                    
                    print("looking state = ",lookingState)
                
                
                        
             # Basic Command => Left ,Right ,Forward 
            if(lookingState==1):   
                if(gaze.is_top()):
                    text = " we will stop"
                    pygame.mixer.music.load("/home/pi/Desktop/direction/stop.wav")
                    pygame.mixer.music.play()
                    ser.write(b"0000\n")#top
                    lookingState=0
                    countblink=0
                    i=0
                    conterFlag=False

                elif(gaze.is_right()):
                    text = "looking right"
                    if(state != 1_1):
                        startTime=time.time()
                        state=1_1
                    if(curentTime - startTime >= 1):
                        text = " we will right"
                        pygame.mixer.music.load("/home/pi/Desktop/direction/right.wav")
                        pygame.mixer.music.play()
                        ser.write(b"0010\n")#RIGHT
                        rightLeft = True
                        lookingState=0
                        conterFlag=False
                        
                elif(gaze.is_center()):
                    text = "looking center"
                    if(state != 1_2):
                        startTime=time.time()
                        state=1_2
                    if((curentTime - startTime >= 2) and (not eyeClose)): 
                        text = " we will go forward"
                        pygame.mixer.music.load("/home/pi/Desktop/direction/forward.wav")
                        pygame.mixer.music.play()
                        rightLeft = False
                        ser.write(b"1010\n") #FORWARD
                        time.sleep(1)
                        lookingState=0
                        conterFlag=False
                
                elif(gaze.is_left()):
                    text = "looking left"
                    if(state != 1_3):
                        startTime=time.time()
                        state=1_3
                    if(curentTime - startTime >= 1):
                        text = " we will turn left now"
                        pygame.mixer.music.load("/home/pi/Desktop/direction/left.wav")
                        pygame.mixer.music.play()
                        ser.write(b"1000\n")#LEFT
                        rightLeft = True
                        time.sleep(1)
                        lookingState=0
                        #countblink=0  
                        conterFlag=False
                
                if(gaze.is_blinking()==1 and rightLeft):
                    text = "close"
                    pygame.mixer.music.load("/home/pi/Desktop/direction/stop.wav")
                    pygame.mixer.music.play()
                    ser.write(b"0000\n")#STOP
                    time.sleep(1)
                    rightLeft=False

                
            elif(lookingState==2):
                if(gaze.is_left()):
                    text = "looking left"
                    if(state != 2_1):
                        startCommandTime=time.time()
                        state=2_1
                    if(curentTime - startCommandTime >= 1):
                        text = " we will go backword"
                        pygame.mixer.music.load("/home/pi/Desktop/direction/backward.wav")
                        pygame.mixer.music.play()
                        ser.write(b"0101\n")#left
                        time.sleep(1)
                        countblink=0
                        i=0
                        lookingState=0
                        conterFlag=False
                
            cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)
            cv2.putText(frame ,"blinking number: " +str(countblink),(90,100),cv2.FONT_HERSHEY_DUPLEX,0.9 ,(147,58,31),1)

            cv2.imshow("Demo",frame)

            if cv2.waitKey(1) == 27:
                break
            
        
    except KeyboardInterrupt:
        pass

webcam.release()
cv2.destroyAllWindows()

