import asyncio
import websockets
import base64
import time
import requests
import json
import subprocess
import config
from ThingsAPI import *
#from composition import composition_mdp


async def Orchestrator():
    print("Opening websocket endpoint...")
    uri = "wss://things.eu-1.bosch-iot-suite.com/ws/2"
    async with websockets.connect(uri, extra_headers=websockets.http.HEADERS({'Authorization': 'Bearer ' + getToken()})) as websocket:
        print("Collecting problem data...")


       
    #current_mdp_state= mdp.initial_state
    #policy= mdp.get_policy_with_value_iteration()
    #next_target_action= target.get_action()
    #while true:
        #current_mdp_state=(current_target_state, current_system_state, next_target_action)
        #service_to_be_assigned=policy[current_mdp_state]

        #next_target_action=target.get_action()

result = asyncio.get_event_loop().run_until_complete(Orchestrator())
while result == 1:
    result = asyncio.get_event_loop().run_until_complete(Orchestrator())
