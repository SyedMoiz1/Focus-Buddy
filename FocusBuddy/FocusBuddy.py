import cv2
from gaze_tracking import GazeTracking
from playsound import playsound
from tkinter import *
from tkinter.font import ITALIC
from datetime import time, datetime, timezone
import os

#creates a window
app = Tk()

app.title('Focus Buddy')
app.geometry('2050x600')
app.configure(bg='light blue')

def close():
    app.destroy()

def retrieve_input():
    global studytime_value
    global breaktime_value
    global path_address
    studytime_value =  studytime_entry.get()
    breaktime_value =  breaktime_entry.get()
    path_address = path_entry.get()
    print(studytime_value, breaktime_value, path_address)       
    close()

def play_game():
    print('play game')
    global isgame
    global path_entry
    path_label.config(text='Enter the game path', bg='light blue' ,font=('arial',12 ,'bold'), pady=40, padx=20)
    path_entry= Entry(app, textvariable=path_text)
    path_entry.grid(row = 6, column = 4)
    isgame = 1

def play_browser():
    print('play browser')
    global isgame
    global path_entry
    path_label.config(text='Enter the browser link',bg='light blue' , font=('arial',12,'bold'), pady=40, padx=20)
    path_entry= Entry(app, textvariable=path_text)
    path_entry.grid(row = 6, column = 4)
    isgame = 0

#title
studytime_text=StringVar()
studytime_label=Label(app, text='Focus Buddy',bg='light blue' ,font=('arial',20,'italic'), pady=30, padx=50)
studytime_label.grid(row=0, column=2, )

#study time
studytime_text=StringVar()
studytime_label=Label(app, text='How long do you want to study for? (minutes)',bg='light blue' ,font=('arial',12,'bold'), pady=20, padx=20)
studytime_label.grid(row=1, column=0, sticky=W)
studytime_entry= Entry(app, textvariable=studytime_text)
studytime_entry.grid(row=1, column=4,)

#break time
breaktime_text=StringVar()
breaktime_label=Label(app, text='How long would you like your break? (minutes)',bg='light blue' ,font=('arial',12,'bold'), pady=40, padx=20)
breaktime_label.grid(row=2, column=0, sticky=W)
breaktime_entry= Entry(app, textvariable=breaktime_text)
breaktime_entry.grid(row=2, column=4,)

#break activity
break_activity_text=StringVar()
break_activity_label=Label(app, text='What would you like to do on your break?',bg='light blue' ,font=('arial',12,'bold'),padx=10, pady=20,)
break_activity_label.grid(row=4, column=0,sticky=W )

# button for break activity
playgame_btn = Button(app, text='Play a game', width=12, command=play_game )
playgame_btn.grid(row=4, column =3)

browser_btn = Button(app, text='Use the browser', width=12, command=play_browser)
browser_btn.grid(row=4, column =4)

path_text=StringVar()
path_label=Label(app, text='',bg='light blue' ,font=('arial',12,'bold'),pady=40, padx=20)
path_label.grid(row=6, column=0, sticky=W)

enter_btn = Button(app, text='Enter',bg="green" ,command=lambda: retrieve_input())
enter_btn.grid(row=7, column =5)

#program starts here
app.mainloop()

###################################################################################

#gets the current time
def currenttime():
    global currentHour
    global currentMinutes

    allTemp = datetime.now(timezone.utc)
    currentHour = allTemp.hour - 5
    currentMinutes = allTemp.minute

#gets the times when the break/study period ends
def timeGet():
    global finHour 
    global finMinute
    global finHour2
    global finMinute2

    print(studytime_value)
    studyMinutes = int(studytime_value) % 60
    studyHours = (int(studytime_value) - studyMinutes) / 60

    breakMinutes = int(breaktime_value) % 60
    breakHours = (int(breaktime_value) - breakMinutes) / 60

    print('Current time is %d:%02d' % (currentHour, currentMinutes))

    print('Study time is: %d:%d' % (studyHours, studyMinutes))

    finHour = (currentHour + studyHours) % 24
    finMinute = currentMinutes + studyMinutes
    if (finMinute >= 60):
        finMinute = finMinute - 60
        finHour = finHour + 1
    print('Study Finish time = %d:%02d' % (finHour, finMinute))

    finHour2 = (finHour + breakHours) % 24
    finMinute2 = finMinute + breakMinutes
    if (finMinute2 >= 60):
        finMinute2 = finMinute2 - 60
        finHour2 = finHour2 + 1
    print('Break Finish time = %d:%02d' % (finHour2, finMinute2))

########################################################################################################

focusCount = 0

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

currenttime()
timeGet()

while True:
    while  (currentHour != finHour) or (currentMinutes != finMinute):
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Not Looking"
            focusCount += 1
        elif gaze.is_right():
            text = "Lost focus (right)"
            focusCount += 1
        elif gaze.is_left():
            text = "Lost focus (left)"
            focusCount += 1
        elif gaze.is_up():
            text = "Lost Focus (up)"
            focusCount += 1
        elif gaze.is_center():
            text = "Focused"
            #back on task so the focus counter returns to 0
            focusCount = 0

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        #counts to frames to see if off task
        if focusCount == 30:
            print("Off task")
            playsound("vineboom.mp3")
            playsound("offtask.mp3")
            playsound("vineboom.mp3")

        cv2.imshow("FocusBuddy", frame)

        #breaks when escape is pressed
        if cv2.waitKey(1) == 27:
            break

        currenttime()

    cv2.destroyAllWindows()

    #runs game/website on break
    if isgame == 1:
        print("Running Game")
        try:
            os.system(path_address)
        finally:
            print("Cannot Run File")
    else:
        print("Running Website")
        os.system("xdg-open " + path_address)

    while(currentHour != finHour2) or (currentMinutes != finMinute2):
        currenttime()

    print("Break Over")

    currenttime()
    timeGet()