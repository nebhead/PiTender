#!/usr/bin/python3

# PiTender Flask/Python script

from flask import Flask, request, render_template, make_response
import time
import os
import json
import datetime

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():

	settings = ReadSettings()
	drink_db = ReadDrinkDB()

	drinklist = {}
	num_drinks = 0

 	# Build a list of drinks based on the available ingredients

	# Cycle through each drink recipe
	for drink_name, drink_details in drink_db['drinks'].items():

		# Cycle through each ingredient in the drink recipe
		for drink_ingredients in drink_details['ingredients'].items():
			matched_ingredient = False

			# Cycle through each ingredient in the inventory and check against the recipe
			for ingredients_available in settings['inventory'].items():
				if (ingredients_available[1] == drink_ingredients[0]):
					matched_ingredient = True
			if(matched_ingredient == False):
				# If even one ingredient is missing from current inventory, then break from loop
				break

		if(matched_ingredient == True):
			# + All ingredients available, storing in drinklist.
			drinklist[drink_name] = drink_db['drinks'][drink_name]
			num_drinks += 1
		# else:
			# - Missing ingredients, not storing in drinklist.

	if (drinklist != {}):
		# Viable drink recipes were found and the list has been created.
		errorcode = 0
	else:
		# No viable drink recipes were found and the list has been created as below.
		drinklist['empty'] = {
			"empty": {
				"name": "No Drink Options",
				"description": "Sorry, it looks like you don't have any drink options with current ingredients.",
				"image": "empty.jpg",
				"ingredients": {
					"none": 0,
				}
			}
		}
		num_drinks = 1
		errorcode = 1

	return render_template('index.html', drinklist=drinklist, num_drinks=num_drinks, errorcode=errorcode)

@app.route('/work/<action>', methods=['POST','GET'])
@app.route('/work', methods=['POST','GET'])
def do_work(action=None):

	status = ReadStatus()
	drink_db = ReadDrinkDB()

	if (action == "cancel"):
		status['control']['stop'] = 1
		print ('Cancel Requested, stop = ' + str(status['control']['stop']) )
		WriteStatus(status)
		return render_template('work.html', action=action)

	if (request.method == 'POST') and (status['status']['active'] == 0):
		response = request.form
		if(response['makedrink'] in drink_db.get('drinks', {})):
			drink_name = response['makedrink']
			#DEBUGprint (drink_name)
			status['status']['active'] = 0
			status['status']['progress'] = 0
			status['control']['start'] = 1
			status['control']['pause'] = 0
			status['control']['stop'] = 0
			status['control']['clean'] = 0
			status['control']['drink_name'] = drink_name
			WriteStatus(status)
			return render_template('work.html', drink_name=drink_name)

	return()


@app.route('/data/<action>', methods=['POST','GET'])
@app.route('/data', methods=['POST','GET'])
def data_dump(action=None):

	status = ReadStatus()
	percent_done = status['status']['progress']
	percent_done_text = str(percent_done) + "%"
	if (status['control']['clean'] > 0):
		mode = 'clean'
	else:
		mode = 'dispense'

	return render_template('data.html', percent_done=percent_done, percent_done_text=percent_done_text, mode=mode)


@app.route('/admin/<action>', methods=['POST','GET'])
@app.route('/admin', methods=['POST','GET'])
def admin(action=None):
	settings = ReadSettings()
	drink_db = ReadDrinkDB()
	status = ReadStatus()
	# List of available BCM.GPIO assignments where 0 is unassigned
	available_GPIOs = [0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]
	errorcode = 0
	errormessage = []

	if (request.method == 'POST') and (action == 'settings'):
		response = request.form
		#DEBUGprint('Settings Change Requested.')
		#DEBUGprint(response)
		for pump_number, pin_number in settings['assignments'].items():
			index = 'inv_' + pump_number
			if(index in response):
				#DEBUGprint(response[index])
				settings['inventory'][pump_number] = response[index]

		for pump_number, inv_name in settings['inventory'].items():
			index = 'ass_' + pump_number
			if(index in response):
				#DEBUGprint(response[index])
				settings['assignments'][pump_number] = int(response[index])

		duplicated_pin = []
		for pump_number, pin_number in settings['assignments'].items():
			for pump_number_inside, pin_number_inside in settings['assignments'].items():
				if (pin_number != 0) and (pin_number == pin_number_inside) and (pump_number != pump_number_inside):
					errorcode = 1
					if (pin_number not in duplicated_pin):
						duplicated_pin.append(pin_number)
						errormessage.append('Pin ' + str(pin_number) + ' is assigned to more than one pump. ')

		if (errorcode > 0):
			settings = ReadSettings()
			errormessage.append('Settings NOT saved. Please check your settings and try again. ')
		else:
			WriteSettings(settings)

	if (request.method == 'POST') and (action == 'clean'):
		response = request.form
		drink_name = 'clean'

		print('Clean Requested.')
		print(response['clean'])
		if 'pump_42' in response['clean']:
			print('Clean ALL pumps for 20 seconds.')
			status['status']['active'] = 0
			status['status']['progress'] = 0
			status['control']['start'] = 0
			status['control']['pause'] = 0
			status['control']['stop'] = 0
			status['control']['clean'] = 42
			status['control']['drink_name'] = 'empty'
			WriteStatus(status)
			return render_template('work.html', drink_name=drink_name)
		else:
			for pump_number, pin_number in settings['assignments'].items():
				if(pump_number in response['clean']):
					print('Clean ' + pump_number + ' for 20 seconds.')
					status['status']['active'] = 0
					status['status']['progress'] = 0
					status['control']['start'] = 0
					status['control']['pause'] = 0
					status['control']['stop'] = 0
					status['control']['clean'] = int(pump_number[-1:])
					status['control']['drink_name'] = 'empty'
					WriteStatus(status)
			return render_template('work.html', drink_name=drink_name)

	if action == 'reboot':
		event = "Admin: Reboot"
		os.system("sleep 3 && sudo reboot &")
		return render_template('shutdown.html', action=action)

	elif action == 'shutdown':
		event = "Admin: Shutdown"
		os.system("sleep 3 && sudo shutdown -h now &")
		return render_template('shutdown.html', action=action)

	uptime = os.popen('uptime').readline()

	cpuinfo = os.popen('cat /proc/cpuinfo').readlines()

	ifconfig = os.popen('ifconfig').readlines()

	temp = checkcputemp()

	return render_template('admin.html', action=action, errorcode=errorcode, errormessage=errormessage, uptime=uptime, cpuinfo=cpuinfo, temp=temp, ifconfig=ifconfig, settings=settings, drink_db=drink_db, available_GPIOs=available_GPIOs)

@app.route('/manifest')
def manifest():
    res = make_response(render_template('manifest.json'), 200)
    res.headers["Content-Type"] = "text/cache-manifest"
    return res

def checkcputemp():
	temp = os.popen('vcgencmd measure_temp').readline()
	return temp.replace("temp=","")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
