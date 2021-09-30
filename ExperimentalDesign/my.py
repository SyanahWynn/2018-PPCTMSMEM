#!/usr/bin/env python
# -*- coding: utf-8 -*-
# My functions.
  
from psychopy import core, visual, event, clock
import csv, os, time
from psychopy import prefs
prefs.general['audioLib'] = ['pyo']
from psychopy import sound
 
## Function section
def getCharacter(window, question="Press any key to continue"):
	message = visual.TextStim(window, text=question)
	message.draw()
	window.flip()
	c = event.waitKeys()
	if c:
		return c[0]
	else:
		return ''
	
    
    
def introScreen(window, question="Press any key to continue"):
    message = visual.TextStim(window, text=question)
    message.draw()
    window.flip()
    core.wait(3.000)
    c = event.waitKeys()
    if c:
        return c[0]
    else:
        return ''
    
    
    
def blankScreen(window, wait = 1.0, text = ""):
	"""Wait for a specified amount of seconds."""
	message = visual.TextStim(window, text=text)
	message.draw()
	window.flip()
	c = event.waitKeys(maxWait=wait, keyList = [])
    

def restEEG(window, waitTime, nrtimes):
     ## VARIABLES ##
    waitTime = 2.000 # 1 min
    loops = 2 # amount of eyes opene eyes closed loops

    # loop over the loops
    for loop in xrange(nrtimes):
        # show instruction to participant for a certain amount of seconds
        tone = sound.Sound(value='C', secs=0.5, octave=4, sampleRate=44100, bits=16)
        tone.setVolume(0.5)
        tone.play()
        message = visual.TextStim(window, text="open uw ogen")
        message.draw()
        window.flip()
        core.wait(waitTime)
        # show instruction to participant for a certain amount of seconds
        message = visual.TextStim(window, text="sluit uw ogen")
        message.draw()
        window.flip()
        core.wait(waitTime) 

def openDataFile(ppn=0):
	"""open a data file for output with a filename that nicely uses the current date and time"""
	directory= "data"
	if not os.path.isdir(directory):
		os.mkdir(directory)
	try:
		filename="{}/{}_{}.dat".format(directory, ppn, time.strftime('%Y-%m-%dT%H:%M:%S')) # ISO compliant
		datafile = open(filename, 'wb')
	except Exception as e:
		filename="{}/{}_{}.dat".format(directory, ppn, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
		datafile = open(filename, 'wb')
	return datafile

def openCSVFile(ppn=0):
	"""open a data file for output with a filename that nicely uses the current date and time"""
	directory= "data"
	if not os.path.isdir(directory):
		os.mkdir(directory)
	try:
		filename="{}/{}_{}.csv".format(directory, ppn, time.strftime('%Y-%m-%dT%H:%M:%S')) # ISO compliant
		datafileCSV = open(filename, 'wb')
	except Exception as e:
		filename="{}/{}_{}.csv".format(directory, ppn, time.strftime('%Y-%m-%dT%H.%M.%S')) #for MS Windows
		datafileCSV = open(filename, 'wb')
	return datafileCSV
	

def getYN(window, question="Y or N"):
	"""Wait for a maximum of two seconds for a y or n key."""
	message = visual.TextStim(window, text=question)
	message.draw()
	window.flip()
	c = event.waitKeys(maxWait=2.0, keyList = ['y', 'n'])
	if c:
		return c[0]
	else:
		return ''

def getString(window, question="Type: text followed by return"):
	string = ""
	while True:
		message = visual.TextStim(window, text=question+"\n"+string)
		message.draw()
		window.flip()
		c = event.waitKeys()
		if c[0] == 'return':
			return string
		else:
			string = string + c[0]
			
lookup = {
          'space': ' ', 
    'exclamation': '!', 
    'doublequote': '"', 
          'pound': '#', 
         'dollar': '$', 
        'percent': '%', 
      'ampersand': '&', 
     'apostrophe': '\'', 
      'parenleft': '(', 
     'parenright': ')', 
       'asterisk': '*', 
           'plus': '+', 
          'comma': ',', 
          'minus': '-', 
         'period': '.', 
          'slash': '/', 
          'colon': ':', 
      'semicolon': ';', 
           'less': '<', 
          'equal': '=', 
        'greater': '>', 
       'question': '?', 
             'at': '@', 
    'bracketleft': '[', 
      'backslash': '\\', 
   'bracketright': ']', 
    'asciicircum': '^', 
     'underscore': '_', 
      'quoteleft': '`', 
      'braceleft': '{', 
            'bar': '|', 
     'braceright': '}', 
     'asciitilde': '~', 
   'num_multiply': '*', 
        'num_add': '+', 
  'num_separator': ',', 
   'num_subtract': '-', 
    'num_decimal': '.', 
     'num_divide': '/', 
          'num_0': '0', 
          'num_1': '1', 
          'num_2': '2', 
          'num_3': '3', 
          'num_4': '4', 
          'num_5': '5', 
          'num_6': '6', 
          'num_7': '7', 
          'num_8': '8', 
          'num_9': '9', 
      'num_equal': '=', 
}

def getString2(window, question="Type: text followed by return"):
	"""Return a string typed by the user, much improved version."""
	string = ''
	capitalizeNextCharacter = False
	while True:
		message = visual.TextStim(window, text=question+"\n"+string)
		message.draw()
		window.flip()
		c = event.waitKeys()[0]
		if len(c)==1:
			# add normal characters (charcters of length 1) to the string
			if capitalizeNextCharacter:
				string += c.capitalize()
				capitalizeNextCharacter = False
			else:
				string += c
		elif c == 'backspace' and len(string)>0:
			# shorten the string
			string = string[:-1]
		elif c == 'escape':
			# return no string
			return ''
		elif c == 'lshift' or  c == 'rshift':
			# pressing shift will cause precise one character to be capitalized
			capitalizeNextCharacter = True
		elif c == 'return' or c == 'num_enter':
			# return the string typed so far
			return string
		elif c in lookup.keys():
			# add special characters to the string
			string += lookup[c]
		else:
			# ignore other special characters
			pass

			
def showText(window, inputText="Text"):
	message = visual.TextStim(window, alignHoriz="center", text=inputText)
	message.draw()
	window.flip()


    
    
def getStimulusInputFile(fileName):
	"""Return a list of trials. Each trial is a list of values."""
	# prepare a list of rows
	rows = []
	# open the file
	inputFile = open(fileName, 'rb')
	# connect a csv file reader to the file
	reader = csv.reader(inputFile, delimiter=',')
	# discard the first row, containing the column labels
	reader.next() 
	# read every row as a list of values and append it to the list of rows
	for row in reader:
		rows.append(row)
	inputFile.close()
	return rows

def getStimulusInputFileDict(fileName):
	"""Return a list of trials. Each trial is a dict."""
	# prepare a list of rows
	rows = []
	# open the file
	inputFile = open(fileName, 'rb')
	# connect a csv dict file reader to the file
	reader = csv.DictReader(inputFile, delimiter=';')
	# read every row as a dict and append it to the list of rows
	for row in reader:
		rows.append(row)
	inputFile.close()
	return rows
	

def debugLog(text):
	tSinceMidnight = clock.getTime()%86400
	tSinceWholeHour = tSinceMidnight % 3600
	minutes = tSinceWholeHour / 60
	hours = tSinceMidnight / 3600
	seconds = tSinceMidnight % 60
	#print("log {:02d}:{:02d}:{:2.3f}: {}".format(int(hours), int(minutes), seconds, text))
	print("log {:02d}:{:02d}:{:f}: {}".format(int(hours), int(minutes), seconds, text))

	
#print (getStimulusInputFileLists("template_stimuli.csv"))