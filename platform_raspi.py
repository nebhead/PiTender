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
		# Init GPIO's to default values / behavior
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		self.pump_pins = {}
		for pump_number, pin_number in settings['assignments'].items():
			GPIO.setup(pin_number, GPIO.OUT, initial=1)
			self.pump_pins[pump_number] = pin_number
			print(f"Pin number {pin_number} initialized as output for {pump_number}.  Set to 1. ")

	def ActivatePump(self, pump_number):
		GPIO.output(self.pump_pins[pump_number], 0) # Turn on Relay
		print(f"{pump_number} Pump Activated. Dispensing on pin: {self.pump_pins[pump_number]}")

	def DeActivatePump(self, pump_number):
		GPIO.output(self.pump_pins[pump_number], 1) # Turn off Relay
		print(f"{pump_number} Pump De-Activated. Stopped Dispensing on pin: {self.pump_pins[pump_number]}")

	def GetOutputStatus(self):
		self.current = {}
		for pump_number in self.pump_pins.items():
			self.current[pump_number] = GPIO.input(self.pump_pins[pump_number])
		return self.current

	def Cleanup(self):
		GPIO.cleanup()
