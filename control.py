#!/usr/bin/python3
# *****************************************
# PiTender Control Python script
# *****************************************
#
# Description: This script will dispense beverages.
#
# This script runs as a separate process from the Flask / Gunicorn
# implementation which handles the web interface.
#
# *****************************************

from __future__ import division
import time
import os
import json
import datetime
import RPi.GPIO as GPIO

# *****************************************
# Supporting Functions
# *****************************************

def WriteLog(event):
	# *****************************************
	# Function: WriteLog
	# Input: str event
	# Description: Write event to event.log
	#  Event should be a string.
	# *****************************************
	now = str(datetime.datetime.now())
	now = now[0:19] # Truncate the microseconds

	logfile = open("./logs/events.log", "a")
	logfile.write(now + ' ' + event + '\n')
	logfile.close()

def ReadStatus():
	# *****************************************
	# Read State Values from File
	# *****************************************
	try:
		json_data_file = open("status.json", "r")
		json_data_string = json_data_file.read()
		status = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one

		status = {}

		status['status'] = {
			"active": 0,
			"progress": 0
			}

		status['control'] = {
			"start": 0,
			"pause": 0,
			"stop": 0
			}

		WriteStatus(status)

	return(status)

def WriteStatus(status):
	# *****************************************
	# Write State Values to File
	# *****************************************
	json_data_string = json.dumps(status)
	with open("status.json", 'w') as status_file:
	    status_file.write(json_data_string)

def ReadSettings():
	# *****************************************
	# Read Settings from File
	# *****************************************

	# Read all lines of settings.json into an list(array)
	try:
		json_data_file = open("settings.json", "r")
		json_data_string = json_data_file.read()
		settings = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one

		settings = {}

		settings['inventory'] = {
			"pump_01": "rum",
			"pump_02": "vodka",
			"pump_03": "whiskey",
			"pump_04": "coke",
			"pump_05": "oj",
			"pump_06": "tequila",
			"pump_07": "marg_mix",
			"pump_08": "iced_tea"
			}

		settings['assignments'] = {
			"pump_01": 17,
			"pump_02": 27,
			"pump_03": 22,
			"pump_04": 23,
			"pump_05": 24,
			"pump_06": 25,
			"pump_07": 0,
			"pump_08": 0
			}

		WriteSettings(settings)

	return(settings)

def WriteSettings(settings):
	# *****************************************
	# Write all settings to JSON file
	# *****************************************
	json_data_string = json.dumps(settings)
	with open("settings.json", 'w') as settings_file:
	    settings_file.write(json_data_string)

def ReadDrinkDB():
	# *****************************************
	# Read Settings from File
	# *****************************************

	# Read all lines of settings.json into an list(array)
	try:
		json_data_file = open("drink_db.json", "r")
		json_data_string = json_data_file.read()
		drink_db = json.loads(json_data_string)
		json_data_file.close()
	except(IOError, OSError):
		# Issue with reading states JSON, so create one/write new one

		drink_db = {}

		drink_db['drinks'] = {
			"empty": "Empty"
			}

		drink_db['ingredients'] = {
			"empty": "Empty",
			}

	return(drink_db)

def WriteLog(event):
	# *****************************************
	# Function: WriteLog
	# Input: str event
	# Description: Write event to event.log
	#  Event should be a string.
	# *****************************************
	now = str(datetime.datetime.now())
	now = now[0:19] # Truncate the microseconds

	logfile = open("./logs/events.log", "a")
	logfile.write(now + ' ' + event + '\n')
	logfile.close()

def PourDrink(drink_name):
	drink_db = ReadDrinkDB()

	if (drink_name in drink_db['drinks']):
		# Set Active Status
		status = ReadStatus()
		status['status']['active'] = 1
		WriteStatus(status)

		total_runtime = 0
		percent_progress = 0
		current_count = 0

		# Cycle through each ingredient in the drink recipe to get the total runtime
		for drink_ingredient, pump_runtime in drink_db['drinks'][drink_name]['ingredients'].items():
			total_runtime = total_runtime + int(pump_runtime)

		# Cycle through each ingredient and dispense the beverage
		for drink_ingredient, pump_runtime in drink_db['drinks'][drink_name]['ingredients'].items():
			if (status['control']['stop'] == 0):
				ActivatePump(drink_ingredient)
				for x in range(int(pump_runtime/5)):
					current_count += 5
					status = ReadStatus()
					if (status['control']['stop'] == 0):
						percent_progress = int((current_count / total_runtime) * 100)
						status['status']['progress'] = percent_progress
						WriteStatus(status)
						time.sleep(5)
					else:
						break
				DeActivatePump(drink_ingredient)
			else:
				break

		status['status']['active'] = 0
		status['control']['start'] = 0
		status['control']['stop'] = 0
		WriteStatus(status)

	else:
		print('Error, no drinks match that name.')

def InitGPIO(settings):
	# Init GPIO's to default values / behavior
	GPIO.setmode(GPIO.BCM)
	for pump_number, pin_number in settings['assignments'].items():
		GPIO.setup(pin_number, GPIO.OUT, initial=0)
		#DEBUGprint('Pin number ' + str(pin_number) + ' initialized as output for ' + pump_number + '.  Set to 1. ')

def ActivatePump(ingredient_name):
	settings = ReadSettings()
	InitGPIO(settings)
	for pump_number, ingredient in settings['inventory'].items():
		if (ingredient == ingredient_name):
			#DEBUGprint(pump_number + " Pump Activated. Dispensing " + ingredient)
			GPIO.output(settings['assignments'][pump_number], 1) # Turn on Relay

def DeActivatePump(ingredient_name):
	settings = ReadSettings()
	InitGPIO(settings)
	for pump_number, ingredient in settings['inventory'].items():
		if (ingredient == ingredient_name):
			#DEBUGprint(pump_number + " Pump De-Activated. Stopped dispensing " + ingredient)
			GPIO.output(settings['assignments'][pump_number], 0) # Turn on Relay

def CleanPump(pump_selected):
	settings = ReadSettings()
	status = ReadStatus()
	status['status']['active'] = 1
	WriteStatus(status)

	if pump_selected > 0 and pump_selected < 9:
		pump_string = 'pump_0' + str(pump_selected)
		for pump_number, pin_number in settings['assignments'].items():
			if (pump_string == pump_number):
				ActivatePump(settings['inventory'][pump_number])
				for index in range(21):
					status = ReadStatus()
					if (status['control']['stop'] == 0):
						status['status']['progress'] = index*5
						WriteStatus(status)
						time.sleep(1) # Run for X seconds
					else:
						break
				DeActivatePump(settings['inventory'][pump_number])

	elif pump_selected == 42:
		total_runtime = 0
		progress = 0

		for pump_number, pin_number in settings['assignments'].items():
			if pin_number != 0:
				total_runtime += 20

		for pump_number, pin_number in settings['assignments'].items():

			if (pin_number != 0) and (status['control']['stop'] == 0):
				ActivatePump(settings['inventory'][pump_number])
				for index in range(20):
					status = ReadStatus()
					if (status['control']['stop'] == 0):
						progress += 1
						status['status']['progress'] = int(100 * (progress / total_runtime))
						WriteStatus(status)
						time.sleep(1) # Run for X seconds
					else:
						break
				DeActivatePump(settings['inventory'][pump_number])

	status['status']['active'] = 0
	status['control']['stop'] = 0
	status['control']['clean'] = 0
	WriteStatus(status)


# *****************************************
# Main Program Loop
# *****************************************

try:
	while True:
		status = ReadStatus()

		if status['status']['active'] == 0:
			if status['control']['start'] == 1:
				event = 'Drink requested: ' + status['control']['drink_name']
				WriteLog(event)
				PourDrink(status['control']['drink_name'])
			elif status['control']['clean'] == 42:
				event = 'Clean requested for all pumps. (code: 42)'
				WriteLog(event)
				CleanPump(42)
			elif status['control']['clean'] > 0:
				event = 'Clean requested for pump: ' + str(status['control']['clean'])
				WriteLog(event)
				CleanPump(status['control']['clean'])

		time.sleep(1)

except:
	GPIO.cleanup()
	print("Cleaning Up & Exiting...")
	quit()
