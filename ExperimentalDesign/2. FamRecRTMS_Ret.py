#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FamRecEEG task details

Encoding stimuli: 450 words
Encoding blocks: 2
Encoding stimulus time: 2 sec
Encoding fixation time: 1 sec
Encoding total duration: min 23.5 min
Retrieval stimuli: 900 words (450 old, 450 new)
Retrival blocks: 3
Retrieval stimulus time: 2 sec
Retrieval fixation time: 1 sec
Retrieval confidence judgement time: 1.5 sec
Retrieval total duration: min 69 min
"""

from psychopy import core, clock, visual, event, sound
import csv, random
import my # import my own functions
import pip
import os
from rusocsci import buttonbox
from psychopy import prefs
prefs.general['audioLib'] = ['pyo']
from psychopy import sound

## Setup Section

#VARIABLES
blocks = 6
stimdur = 2
fixdur = 1
confdur = 1.5
practrials = 20
rettrials = 900

win = visual.Window([800,600], fullscr=True, monitor="testMonitor", units='cm',allowGUI=False)
#win = visual.Window([800,600], fullscr=False, monitor="testMonitor")

# get info for this participant
session = my.getString(win, "Please enter session number:")
ppn = my.getString(win, "Please enter participant number:")
gender = my.getString(win, "Please enter participant gender:")
age = my.getString(win, "Please enter participant age:")

# determine inputfile
inputfile = "SubjectFiles/" + ppn + "_session" + session + "_ret.csv"

# read stimuli file
trials = my.getStimulusInputFile(inputfile)
wordsColumn = 0     #number = trials[trialNumber][numberColumn]
classColumn = 2       #name = trials[trialNumber][nameColumn]

# turn the text strings into stimuli
textStimuli = []
for trial in trials:
    # append this stimulus to the list of prepared stimuli
    textStimuli.append(visual.TextStim(win, text=trial[wordsColumn])) 
    #imageStimuli.append(visual.ImageStim(win=window, size=[0.5,0.5], image="image/"+row[0]))
    #soundStimuli.append(visual.ImageStim(win=window, size=[0.5,0.5], image="image/"+row[0]))

#fixation cross
fixation = visual.ShapeStim(win, 
    vertices=((0, -0.3), (0, 0.3), (0,0), (-0.3,0), (0.3, 0)),
    lineWidth=2,
    closeShape=False,
    lineColor='white'
)

# open data output file
datafile = my.openDataFile(ppn + "_session_" + session + "_ret")
datafileCSV = my.openCSVFile(ppn + "_session_" + session + "_ret")
libraryfile = my.openDataFile(ppn + "_session_" + session + "_ret" + "_library")
# connect it with a csv writer
writer = csv.writer(datafile, delimiter=";")
writerCSV = csv.writer(datafileCSV, delimiter=",")
tempwriter = csv.writer(libraryfile, delimiter=";")
# create output file header
writerCSV.writerow([
    "ppn", 
    "gender",
    "age",
    "word", 
    "Retrieval_Session", 
    "OldNew_Classification",
    "OldNew_Response",  
    "OldNew_RT",
    "OldNew_Accuracy",
    "Conficence_Response",  
    "Confidence_RT",
    "Confidence_Rating",
    "fixationTime", 
    ])
writer.writerow([
    "ppn", 
    "gender",
    "age",
    "word", 
    "Retrieval_Session", 
    "OldNew_Classification",
    "OldNew_Response",  
    "OldNew_RT",
    "OldNew_Accuracy",
    "Conficence_Response",  
    "Confidence_RT",
    "Confidence_Rating",
    "fixationTime", 
    ])
tempwriter.writerow([__file__])
for pkg in pip.get_installed_distributions():
    tempwriter.writerow([pkg.key, pkg.version])
 
## Experiment Section

# show welcome screen
my.introScreen(win, "U krijgt straks weer woorden te zien op het scherm. Heeft u het woord in het eerste deel gezien (oud), drukt u op het pijltje naar links, heeft u het woord niet in het eerste deel gezien (nieuw), drukt u op het pijltje naar rechts. \n\noud <--\nnieuw -->")
my.introScreen(win, "Na het woord verschijnt een nieuw scherm. Op dit scherm wordt u gevraagd aan te geven hoe zeker u bent van uw voorgaande 'oud/nieuw' keuze. \n\nniet zeker   links\nbeetje zeker   beneden \nheel zeker   rechts")
startTime = clock.getTime() # clock is in seconds
i=0
while i < len(trials):
    if i == 0:
        print("start practice")
    if i == practrials:
        my.blankScreen(win)
        answer = my.getCharacter(win, "Dit is het einde van het oefenblok, wilt u nog een keer oefenen? [j/n]")
        if answer[0] == "j":
            i=0
        elif answer[0] == "n":
            i=i
    if (i == rettrials/blocks or 
            i == rettrials/blocks*2 or
            i == rettrials/blocks*3 or
            i == rettrials/blocks*4 or
            i == rettrials/blocks*5):
        my.blankScreen(win, wait = 60.000, text = "Pauze!")
        my.getCharacter(win, "druk op een knop om door te gaan")

    trial = trials[i]
    
    # present fixation
    fixation.draw()
    win.flip()
    fixationTime = clock.getTime()
    core.wait(0.993) # note how the real time will be very close to a multiple of the refresh time
    
    # present stimulus text and wait a maximum of 2 second for a response
    textStimuli[i].draw()
    win.flip()
    textTime = clock.getTime()
    key = event.waitKeys(stimdur, keyList=['left', 'right','escape'])
    if key != None:
        responseTime = clock.getTime()
    else:
        responseTime = textTime
    while clock.getTime() < (textTime + stimdur):
        pass
    oldNewTime = clock.getTime()
    
    #present confidence judgement screen if there was an old/new response
    if key != None:
        visual.TextStim(win, text="Hoe zeker?").draw()
        win.flip()
        conf = event.waitKeys(confdur, keyList=['left', 'down', 'right', 'escape'])
        if conf != None:
            conf_rt = clock.getTime()
        else:
            conf_rt = oldNewTime
        while clock.getTime() < (oldNewTime+ confdur):
            pass
    else:
        conf = []
        conf.append("")
        conf_rt = oldNewTime

    # write result to data file
    if key==None:
        key=[]
        key.append("")
    if conf==None:
        conf=[]
        conf.append("")
        
    if (trial[classColumn] == "1" and key[0] == 'left'): #old & old
        acc = 11 #hit
    elif (trial[classColumn] == "1" and key[0] == 'right'): #old & new
        acc = 12 #miss
    elif (trial[classColumn] == "2" and key[0] == 'left'): #new & old
        acc = 21 # false alarm
    elif (trial[classColumn] == "2" and key[0] == 'right'): #new & new
        acc = 22 #correct rejection
    else:
        acc = 99 # no response
    
    if (key[0] == 'left' and conf[0] == 'left'): #old & 1
        Confidence_Rating = 11 #not sure old
    elif (key[0] == 'left' and conf[0] == 'down'): #old & 2
        Confidence_Rating = 12 #bit sure old
    elif (key[0] == 'left' and conf[0] == 'right'): #old & 3
        Confidence_Rating = 13 # very sure old
    elif (key[0] == 'right' and conf[0] == 'left'): #new & 1
        Confidence_Rating = 21 #not sure new
    elif (key[0] == 'right' and conf[0] == 'down'): #new & 2
        Confidence_Rating = 22 #bit sure new
    elif (key[0] == 'right' and conf[0] == 'right'): #new & 3
        Confidence_Rating = 23 # very sure new
    else:
        Confidence_Rating = 99 # no response
        
        
    print("{}, text: ,{}, {}, key: {} {} {} {} acc: {} {}".format( i+1, trial[wordsColumn], trial[classColumn],  key, responseTime - textTime, conf, conf_rt - oldNewTime, acc, Confidence_Rating) )

    writer.writerow([
        ppn,
        gender,
        age,
        trial[wordsColumn], 
        session, 
        trial[classColumn],
        key[0],
        "{:.3f}".format(responseTime - textTime),
        acc,
        conf[0], 
        "{:.3f}".format(conf_rt - oldNewTime),
        Confidence_Rating,
        "{:.3f}".format(fixationTime - startTime), 
        ])
    writerCSV.writerow([
        ppn,
        gender,
        age,
        trial[wordsColumn], 
        session, 
        trial[classColumn],
        key[0],
        "{:.3f}".format(responseTime - textTime),
        acc,
        conf[0], 
        "{:.3f}".format(conf_rt - oldNewTime),
        Confidence_Rating,
        "{:.3f}".format(fixationTime - startTime), 
        ])
    
    if key[0]=='escape' or conf[0] == 'escape':
        break
    i = i+1
datafile.close()
datafileCSV.close()

# show goodbye screen
my.showText(win, "Einde van het experiment \n\nBedankt voor het meedoen!")
core.wait(1.000)

## Closing Section
win.close()
core.quit()
