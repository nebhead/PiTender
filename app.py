#!/usr/bin/env python3

# PiTender Flask/Python script

from flask import Flask, flash, url_for, request, render_template, make_response, jsonify, redirect
import time
import os
import json
import datetime
from common import *
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/img/drinks'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def fixup_string(broken):
	fixed = ''.join(e for e in broken if e.isalnum())
	fixed = fixed.lower()
	return(fixed)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploadfile', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		# check if the post request has the file part
		if 'file' not in request.files:
			return redirect('/recipe')
		else:
			file = request.files['file']
			# If the user does not select a file, the browser submits an
			# empty file without a filename.
			if file.filename == '':
				#flash('No selected file')
				return redirect('/recipe')
			if file and allowed_file(file.filename):
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				return redirect('/recipe')
	return redirect('/recipe')

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
		#print ('Cancel Requested, stop = ' + str(status['control']['stop']) )
		WriteStatus(status)
		return render_template('work.html', action=action, workmode='cancel')

	if (request.method == 'POST') and (status['status']['active'] == 0):
		response = request.form
		if(response['makedrink'] in drink_db.get('drinks', {})):
			drink_name = response['makedrink']
			status['status']['active'] = 0
			status['status']['progress'] = 0
			status['control']['start'] = 1
			status['control']['pause'] = 0
			status['control']['stop'] = 0
			status['control']['clean'] = ""
			status['control']['drink_name'] = drink_name
			WriteStatus(status)
			return render_template('work.html', drink_name=drink_name, action="default", workmode='dispense')

	return redirect('/')

@app.route('/workstatus')
def workstatus(action=None):
	status = ReadStatus()
	percent_done = status['status']['progress']

	return jsonify({ 'percent_done' : percent_done })

@app.route('/recipe/<action>', methods=['POST'])
@app.route('/recipe', methods=['POST','GET'])
def recipe(action=None):
	drink_db = ReadDrinkDB()

	UPLOAD_DIR = 'static/img/drinks'

	if (request.method == 'POST'):
		response = request.form
		#print(response)
		# Drink Recipe Edit Functions
		if('drink_edit' in response):
			if (response['drink_edit'] == 'true'):
				#print('drink_edit')
				# Get Selected Drink Recipe
				drink_id = response['drink_id']
				#print(drink_id)
				# Build Image List
				img_list = []
				for root, dirs, files in os.walk(UPLOAD_DIR):
					for file in files:
						if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".jpeg") or file.endswith(".JPEG") or file.endswith(".png"):
							filename = (os.path.join(root, file)).replace('static/','')
							
							#print(filename)
							img_list.append(filename)
				#print(img_list)
				num_imgs = len(img_list)
				return render_template('recipe_drink_edit.html', drink_db=drink_db, drink_id=drink_id, img_list=img_list, num_imgs=num_imgs)
		elif('drink_add' in response):
			if (response['drink_add'] == 'true'):
				#print('drink_add')
				drink_id = 'enter_new_drink_id'
				if (drink_id in drink_db['drinks']):
					# If there was another record with the same name, delete it
					drink_db['drinks'].pop(drink_id)
				drink_db['drinks'][drink_id] = {}
				drink_db['drinks'][drink_id]['name'] = 'DEFAULT Drink Name'  
				drink_db['drinks'][drink_id]['description'] = 'Enter Description.'
				drink_db['drinks'][drink_id]['image'] = 'img/drinks/default.jpg'
				drink_db['drinks'][drink_id]['ingredients'] = {}
				WriteDrinkDB(drink_db)
				# Build Image List
				img_list = []
				for root, dirs, files in os.walk(UPLOAD_DIR):
					for file in files:
						if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".jpeg") or file.endswith(".JPEG") or file.endswith(".png"):
							filename = (os.path.join(root, file)).replace('static/','')
							
							#print(filename)
							img_list.append(filename)
				#print(img_list)
				num_imgs = len(img_list)
				return render_template('recipe_drink_edit.html', drink_db=drink_db, drink_id=drink_id, img_list=img_list, num_imgs=num_imgs)
		elif('drink_del' in response):
			if (response['drink_del'] == 'true'):
				#print('drink_del')
				drink_id = response['drink_id']
				#print(drink_id)
				drink_db['drinks'].pop(drink_id)
				WriteDrinkDB(drink_db)
				return ('{ "result" : "success" }')
		elif('drink_edid' in response):
			if (response['drink_edid'] == 'true'):
				#print('drink_edid')
				drink_id = response['drink_id']
				new_drink_id = response['new_drink_id']
				#print(drink_id)
				if(new_drink_id.isalnum() != True): 
					new_drink_id = fixup_string(new_drink_id)
				drink_db['drinks'][new_drink_id] = drink_db['drinks'].pop(drink_id)
				WriteDrinkDB(drink_db)
				return render_template('recipe_drink_edit.html', drink_db=drink_db, drink_id=new_drink_id)
		elif('drink_dn' in response):
			if (response['drink_dn'] == 'true'):
				#print('drink_dn')
				drink_id = response['drink_id']
				new_drink_dn = response['new_drink_dn']
				#print(drink_id)
				drink_db['drinks'][drink_id]['name'] = new_drink_dn
				WriteDrinkDB(drink_db)
				return ('{ "result" : "success" }')
		elif('drink_desc' in response):
			if (response['drink_desc'] == 'true'):
				#print('drink_desc')
				drink_id = response['drink_id']
				new_drink_desc = response['new_drink_desc']
				#print(drink_id)
				drink_db['drinks'][drink_id]['description'] = new_drink_desc
				WriteDrinkDB(drink_db)
				return ('{ "result" : "success" }')
		elif('drink_ing_edit' in response):
			if (response['drink_ing_edit'] == 'true'):
				#print('drink_ing_edit')
				drink_id = response['drink_id']
				ing_id = response['ing_id']
				return render_template('recipe_drink_ing_edit.html', ingdisplayname=drink_db['ingredients'][ing_id], pumptime=drink_db['drinks'][drink_id]['ingredients'][ing_id], ing_id=ing_id, drink_id=drink_id)
		elif('drink_ing_del' in response):
			if (response['drink_ing_del'] == 'true'):
				#print('drink_ing_del')
				drink_id = response['drink_id']
				ing_id = response['ing_id']
				drink_db['drinks'][drink_id]['ingredients'].pop(ing_id)
				WriteDrinkDB(drink_db)
				return ('{ "result" : "success" }')
		elif('drink_ing_save' in response):
			if (response['drink_ing_save'] == 'true'):
				#print('drink_ing_save')
				drink_id = response['drink_id']
				ing_id = response['ing_id']
				new_pumptime = response['new_pumptime']
				drink_db['drinks'][drink_id]['ingredients'][ing_id] = int(new_pumptime)
				WriteDrinkDB(drink_db)
				return render_template('recipe_drink_ing_saved.html', ing_dn=drink_db['ingredients'][ing_id], pumptime=new_pumptime, ing_id=ing_id, drink_id=drink_id)
		elif('drink_ing_add' in response):
			if (response['drink_ing_add'] == 'true'):
				#print('drink_ing_add')
				drink_id = response['drink_id']
				new_ing_id = response['new_ing_id']
				new_pumptime = response['new_pumptime']
				if (new_ing_id in drink_db['ingredients']):
					drink_db['drinks'][drink_id]['ingredients'][new_ing_id] = int(new_pumptime)
					WriteDrinkDB(drink_db)
				return render_template('recipe_drink_ing_saved.html', ing_dn=drink_db['ingredients'][new_ing_id], pumptime=new_pumptime, ing_id=new_ing_id, drink_id=drink_id)
		elif('drink_ing_add_init' in response):
			if (response['drink_ing_add_init'] == 'true'):
				drink_id = response['drink_id']
				return render_template('recipe_drink_ing_add.html', drink_id=drink_id, drink_db=drink_db)
		elif('drink_img_sel' in response):
			if (response['drink_img_sel'] == 'true'):
				drink_id = response['drink_id']
				imagefilename = response['image_id']
				drink_db['drinks'][drink_id]['image'] = imagefilename
				WriteDrinkDB(drink_db)

		# Ingredient Edit Functions
		elif('ing_edit' in response):
			if (response['ing_edit'] == 'true'):
				#print ('Edit Selected.')
				id = response['ing_id']
				return render_template('recipe_ing_edit.html', id=id, displayname=drink_db['ingredients'][id])
		elif('ing_del' in response):
			if (response['ing_del'] == 'true'):
				#print ('Delete Selected.')
				id = response['ing_id']
				if(id in drink_db['ingredients']):
					drink_db['ingredients'].pop(id)
					WriteDrinkDB(drink_db)
				return ('Deleting...')
		elif('ing_save' in response):
			if (response['ing_save'] == 'true'):
				#print ('Save Selected.')
				id = response['ing_id']
				new_id = response['ing_new_id']
				new_dn = response['ing_new_dn']
				if new_dn != drink_db['ingredients'][id]:
					drink_db['ingredients'][id] = new_dn
				if new_id != id: 
					if(new_id.isalnum() != True): 
						new_id = fixup_string(new_id)
					drink_db['ingredients'][new_id] = drink_db['ingredients'].pop(id)
				WriteDrinkDB(drink_db)
				return render_template('recipe_ing_save.html', old_id=id, id=new_id, displayname=new_dn)
		elif('ing_add' in response):
			if (response['ing_add'] == 'true'):
				#print ('Add Selected.')
				new_id = response['ing_new_id']
				new_dn = response['ing_new_dn']
				if(new_id.isalnum() != True): 
					new_id = fixup_string(new_id)
				drink_db['ingredients'][new_id] = new_dn
				WriteDrinkDB(drink_db)
				return render_template('recipe_ing_save.html', old_id='ing_row_add', id=new_id, displayname=new_dn)
	return render_template('recipe.html', drink_db=drink_db, selected_drink='none')

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

		if ('flow_rate' in response):
			print(response['flow_rate'])
			settings['flowrate'] = int(response['flow_rate'])

		if (errorcode > 0):
			settings = ReadSettings()
			errormessage.append('Settings NOT saved. Please check your settings and try again. ')
		else:
			WriteSettings(settings)

	if (request.method == 'POST') and (action == 'clean'):
		response = request.form
		drink_name = 'clean'

		#print('Clean Requested.')
		#print(response['clean'])
		if 'pump_42' in response['clean']:
			#print('Clean ALL pumps for 20 seconds.')
			status['status']['active'] = 0
			status['status']['progress'] = 0
			status['control']['start'] = 0
			status['control']['pause'] = 0
			status['control']['stop'] = 0
			status['control']['clean'] = "all"
			status['control']['drink_name'] = 'empty'
			WriteStatus(status)
			return render_template('work.html', drink_name=drink_name, action="default", workmode='clean')
		else:
			for pump_number, pin_number in settings['assignments'].items():
				if(pump_number in response['clean']):
					#print('Clean ' + pump_number + ' for 20 seconds.')
					status['status']['active'] = 0
					status['status']['progress'] = 0
					status['control']['start'] = 0
					status['control']['pause'] = 0
					status['control']['stop'] = 0
					status['control']['clean'] = pump_number
					status['control']['drink_name'] = 'empty'
					WriteStatus(status)
			return render_template('work.html', drink_name=drink_name, action="default", workmode='clean')

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

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True) # Use this for Debug Mode
	app.run(host='0.0.0.0') # Use this for Production Mode
