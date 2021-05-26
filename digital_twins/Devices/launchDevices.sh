#!/bin/bash
python2 bathroom_heating_device.py & disown
python2 bathtub_device.py & disown
python2 door_device.py & disown
python2 kitchen_exhaust_fan_device.py & disown
python2 user_behaviour.py & disown
python2 target.py & disown
