#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
FamRecEEG task details

Encoding stimuli: 450 words
Encoding blocks: 3
Encoding stimulus time: 2 sec
Encoding fixation time: 1 sec
Encoding total duration: min 23.5 min
Retrieval stimuli: 900 words (450 old, 450 new)
Retrival blocks: 6
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
blocks = 3
stimdur = 2
fixdur = 1
practrials = 20
enctrials = 450

win = visual.Window([800,600], fullscr=True, monitor="testMonitor", units='cm',allowGUI=False)
#win = visual.Window([800,600], fullscr=False, monitor="testMonitor")

# get info for this participant
session = my.getString(win, "Please enter session number:")
ppn = my.getString(win, "Please enter participant number:")
gender = my.getString(win, "Please enter participant gender:")
age = my.getString(win, "Please enter participant age:")

# determine inputfile
inputfile = "SubjectFiles/" + ppn + "_session" + session + "_enc.csv"

# read stimuli file
trials = my.getStimulusInputFile(inputfile)
wordsColumn = 0     #number = trials[trialNumber][wordColumn]
stimtype = 2

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
datafile = my.openDataFile(ppn + "_session_" + session + "_enc")
datafileCSV = my.openCSVFile(ppn + "_session_" + session + "_enc")
libraryfile = my.openDataFile(ppn + "_session_" + session + "_enc" + "_library")
# connect it with a csv writer
writer = csv.writer(datafile, delimiter=";")
writerCSV = csv.writer(datafileCSV, delimiter=",")
tempwriter = csv.writer(libraryfile, delimiter=";")
# create output file header
writer.writerow([
    "ppn", 
    "gender",
    "age",
    "word", 
    "session", 
    "pleasure_key",  
    "pleasure_rt",
    "fixationTime", 
    "stimulation",
    ])
writerCSV.writerow([
    "ppn", 
    "gender",
    "age",
    "word", 
    "Encoding_Session", 
    "Encoding_Response",  
    "Encoding_RT",
    "fixationTime", 
    "StimOrder"
    ])
tempwriter.writerow([__file__])
for pkg in pip.get_installed_distributions():
    tempwriter.writerow([pkg.key, pkg.version])


## Experiment Section

# show welcome screen
my.introScreen(win, "U krijgt straks woorden te zien op het scherm. Vindt u het woord plezierig, drukt u op het pijltje naar links, vindt u het woord onplezierig, drukt u op het pijltje naar rechts. \n\nplezierig <--\nonplezierig -->")
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
    if (i == enctrials/blocks or 
            i == enctrials/blocks*2):
        my.blankScreen(win, wait = 60.000, text = "Pauze!")
        my.getCharacter(win, "druk op een knop om door te gaan")

    trial = trials[i]
    
    # present fixation
    fixation.draw()
    win.flip()
    fixationTime = clock.getTime()
    core.wait(fixdur) # note how the real time will be very close to a multiple of the refresh time
    
    # present stimulus text and wait a maximum of stimdur for a response
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

    print("{}, text: {}, key: {}, text: {}".format( i+1, trial[wordsColumn], key, responseTime - textTime) )
    
    # write result to data file
    if key==None:
        key=[]
        key.append("")

    writer.writerow([
        ppn,
        gender,
        age,
        trial[wordsColumn], 
        session, 
        key[0],
        "{:.3f}".format(responseTime - textTime),
        "{:.3f}".format(fixationTime - startTime), 
        trial[stimtype],
        ])
    writerCSV.writerow([
        ppn,
        gender,
        age,
        trial[wordsColumn], 
        session, 
        key[0],
        "{:.3f}".format(responseTime - textTime),
        "{:.3f}".format(fixationTime - startTime), 
        trial[stimtype],
        ])
    
    if key[0]=='escape':
        break
    i = i+1
datafile.close()
datafileCSV.close()

# show goodbye screen
my.showText(win, "Einde van het eerste deel")
core.wait(1.000)
print(trial[stimtype])

## Closing Section
win.close()
core.quit()
