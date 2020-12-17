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

# Set this to False on Raspberry Pi Host ()
prototype_mode = False
#prototype_mode = True # Comment out this line to disable TEST / Prototype mode

# *****************************************
# Imported Libraries
# *****************************************

#from __future__ import division
import time
import os
import json
import datetime
from common import *

if(prototype_mode == True):
	# Prototype Modules for Test Host (i.e. PC based testing)
	from platform_prototype import PumpControl # Library for reading the ADC device
else:
	# Actual Modules for RasPi
	from platform_raspi import PumpControl # Library for reading the ADC device

# *****************************************
# Supporting Functions
# *****************************************

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

		# Initialize Platform Object
		settings = ReadSettings()
		platform = PumpControl(settings)

		# Cycle through each ingredient in the drink recipe to get the total runtime
		for drink_ingredient, pump_runtime in drink_db['drinks'][drink_name]['ingredients'].items():
			total_runtime = total_runtime + int(pump_runtime)

		# Cycle through each ingredient and dispense the beverage
		for drink_ingredient, pump_runtime in drink_db['drinks'][drink_name]['ingredients'].items():
			if (status['control']['stop'] == 0):
				pump_number = 'none'
				for index, value in settings['inventory'].items():
					if(value == drink_ingredient):
						pump_number = index
						print(f'Pump number = {index}')
				platform.ActivatePump(pump_number)
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
				platform.DeActivatePump(pump_number)
			else:
				break

		status['status']['active'] = 0
		status['control']['start'] = 0
		status['control']['stop'] = 0
		WriteStatus(status)

	else:
		print('Error, no drinks match that name.')

def CleanPump(pump_selected):
	settings = ReadSettings()
	status = ReadStatus()
	status['status']['active'] = 1
	WriteStatus(status)

	# Initialize Platform Object
	settings = ReadSettings()
	platform = PumpControl(settings)

	if pump_selected > 0 and pump_selected < 9:
		pump_string = 'pump_0' + str(pump_selected)
		for pump_number, pin_number in settings['assignments'].items():
			if (pump_string == pump_number):
				platform.ActivatePump(pump_number)
				for index in range(21):
					status = ReadStatus()
					if (status['control']['stop'] == 0):
						status['status']['progress'] = index*5
						WriteStatus(status)
						time.sleep(1) # Run for X seconds
					else:
						break
				platform.DeActivatePump(pump_number)

	elif pump_selected == 42:
		total_runtime = 0
		progress = 0

		for pump_number, pin_number in settings['assignments'].items():
			if pin_number != 0:
				total_runtime += 20

		for pump_number, pin_number in settings['assignments'].items():

			if (pin_number != 0) and (status['control']['stop'] == 0):
				platform.ActivatePump(pump_number)
				for index in range(20):
					status = ReadStatus()
					if (status['control']['stop'] == 0):
						progress += 1
						status['status']['progress'] = int(100 * (progress / total_runtime))
						WriteStatus(status)
						time.sleep(1) # Run for X seconds
					else:
						break
				platform.DeActivatePump(pump_number)

	status['status']['active'] = 0
	status['control']['stop'] = 0
	status['control']['clean'] = 0
	WriteStatus(status)


# *****************************************
# Main Program Loop
# *****************************************
def main():
	# Clear all status bits on start up
	status = {}

	status['status'] = {
		"active": 0,
		"progress": 0
		}

	status['control'] = {
		"start": 0,
		"pause": 0,
		"stop": 0,
		"clean": 0,
		"drink_name": ""
		}
	WriteStatus(status)

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
		raise
		print("Cleaning Up & Exiting...")
		quit()

if __name__ == "__main__":
    main()