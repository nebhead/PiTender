#!/usr/bin/env python3

# *****************************************
# PiTender Prototype Interface Library
# *****************************************
#
# Description: This library supports controlling the PiTender in Prototype mode
#
# *****************************************

# *****************************************
# Imported Libraries
# *****************************************
# None

class PumpControl:
    def __init__(self, settings):
		# Init GPIO's to default values / behavior
        self.pump_pins = {}
        self.current = {}
        for pump_number, pin_number in settings['assignments'].items():
            self.pump_pins[pump_number] = pin_number
            self.current[pump_number] = 1
            print(f"Pin number {pin_number} initialized as output for {pump_number}.  Set to 1. ")

    def ActivatePump(self, pump_number):
        if(pump_number in self.current):
            print(f"{pump_number} Pump Activated. Dispensing on pin: {self.pump_pins[pump_number]}")
            self.current[pump_number] = 0
        else:
            print(f"{pump_number} not found. ")

    def DeActivatePump(self, pump_number):
        if(pump_number in self.current):
            print(f"{pump_number} Pump De-Activated. Stopped Dispensing on pin: {self.pump_pins[pump_number]}")
            self.current[pump_number] = 1
        else:
            print(f"{pump_number} not found. ")

    def GetOutputStatus(self):
        return self.current

    def Cleanup(self):
        print('All clean.')
