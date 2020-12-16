#!/usr/bin/env python3

# *****************************************
# PiTender RaspberryPi Interface Library
# *****************************************
#
# Description: This library supports controlling the PiTender outputs via
#  Raspberry Pi GPIOs
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************

import RPi.GPIO as GPIO

class PumpControl:

	def __init__(self, settings):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)

		# Init GPIO's to default values / behavior
		for pump_number, pin_number in settings['assignments'].items():
			GPIO.setup(pin_number, GPIO.OUT, initial=0)
			print('Pin number ' + str(pin_number) + ' initialized as output for ' + pump_number + '.  Set to 1. ')

	def ActivatePump(self, ingredient_name, settings):
		for pump_number, ingredient in settings['inventory'].items():
			if (ingredient == ingredient_name):
				print(pump_number + " Pump Activated. Dispensing " + ingredient)
				GPIO.output(settings['assignments'][pump_number], 1) # Turn on Relay

	def DeActivatePump(self, ingredient_name, settings):
		for pump_number, ingredient in settings['inventory'].items():
			if (ingredient == ingredient_name):
				print(pump_number + " Pump De-Activated. Stopped Dispensing " + ingredient)
				GPIO.output(settings['assignments'][pump_number], 0) # Turn off Relay

	def GetOutputStatus(self, settings):
		self.current = {}
		for pump_number, pin_number in settings['assignments'].items():
			self.current[pump_number] = GPIO.input(pin_number)
		return self.current

	def Cleanup():
		GPIO.cleanup()
