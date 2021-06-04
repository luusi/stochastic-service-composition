from abc import ABC
from typing import Optional
import json

import netifaces
import paho.mqtt.client as mqtt

import datetime, threading, time

from stochastic_service_composition.services import Service
from stochastic_service_composition.types import State, Action

DEVICE_ID_PREFIX = "com.bosch.services"
DITTO_PREFIX = "com.bosch.services/"
TENANT_ID = "t6f04cf30b6b34842bfe43e6d9da37818_hub"
HUB_ADAPTER_HOST = "mqtt.bosch-iot-hub.com"
CERTIFICATE_PATH_ID = "./iothub.crt"
DEVICE_PASSWORD_ID = "secret"
# Configuration of client ID and publish topic
PUBLISH_TOPIC = "telemetry/"
CLIENT = mqtt.Client


class BoschIotDevice(ABC):
    """A Bosch IoT device."""

    def __init__(self, device_name: str,
                 service: Service,
                 certificate_path: str = CERTIFICATE_PATH_ID):
        self._device_name = device_name
        self._service = service
        self._certificate_path = certificate_path

        self._current_state: Optional[State] = self._service.initial_state
        self._is_running: bool = False
        self._terminated = threading.Event()

        self._client = CLIENT(self.client_id)

    def reset(self):
        if self.is_running:
            raise ValueError("cannote reset while running")
        self._current_state = self._service.initial_state

    @property
    def is_running(self):
        """Check whether the device is running."""
        return self._is_running

    @property
    def device_name(self):
        return self._device_name

    @property
    def device_id(self):
        return f"{DEVICE_ID_PREFIX}:{self.device_name}"

    @property
    def tenant_id(self):
        return f"{TENANT_ID}"

    @property
    def hub_adapter_host(self):
        return f"{HUB_ADAPTER_HOST}"

    @property
    def certificate_path(self):
        return self._certificate_path

    @property
    def device_password(self):
        return f"{DEVICE_PASSWORD_ID}"

    @property
    def client_id(self):
        return self.device_id

    @property
    def auth_id(self):
        return f"{DEVICE_ID_PREFIX}_{self.device_name}"

    @property
    def ditto_topic(self):
        return f"{DITTO_PREFIX}/{self.device_name}"

    @property
    def publish_topic(self):
        return f"{PUBLISH_TOPIC}{self.tenant_id}/{self.device_id}"

    def on_connect(self, client, userdata, flags, rc):
        """The callback for when the client receives a CONNACK response from the server."""
        if rc != 0:
            print("Connection to MQTT broker failed: " + str(rc))
            return
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.

        # BEGIN SAMPLE CODE
        client.subscribe("command///req/#")
        # END SAMPLE CODE
        print("Connected!")

    def on_message(self, client, userdata, msg):
        """The callback for when a PUBLISH message is received from the server."""
        print(f"Message received: client={client}, userdata={userdata}, msg={msg}")
        cmd = json.loads(msg.payload.decode("utf-8"))
        cmd_name = cmd["topic"].split("/")[-1]
        print(f"Command: {cmd_name}")
        print(f"Current state: {self._current_state}")
        self.change_status(json.dumps("busy"))
        self.execute_command(cmd_name)
        self.change_status(json.dumps("terminated"))
        print(f"Current state after executing command: {self._current_state}")


    def execute_command(self, name: Action):
        transitions_from_current_state = self._service.transition_function[self._current_state]
        next_state = transitions_from_current_state[name]
        self._current_state = next_state
        self.update_state("current_state", self._current_state)

    def update_state(self, feature, value):
        payload = '{"topic": "' + self.ditto_topic + \
                  '/things/twin/commands/modify","headers": {"response-required": false},' + \
                  '"path": "/features/' + feature + '/properties/value/current","value" : ' + value + '}'
        self._client.publish(self.publish_topic, payload)

    def publish_output(self, output):
        payload = '{"topic": "' + self.ditto_topic + \
                  '/things/twin/commands/modify","headers": {"response-required": false},' + \
                  '"path": "/features/output/properties/value","value" : ' + output + '}'
        self._client.publish(self.publish_topic, payload)

    def change_status(self, status):
        payload = '{"topic": "' + self.ditto_topic + \
                  '/things/twin/commands/modify","headers": {"response-required": false},' + \
                  '"path": "/features/status/properties/value","value" : ' + status + '}'
        self._client.publish(self.publish_topic, payload)

        # Period for publishing data to the MQTT broker in seconds
        #timePeriod = 10

    def run(self):
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message
        self._client.tls_set(self.certificate_path)
        username = self.auth_id + "@" + self.tenant_id
        self._client.username_pw_set(username, self.device_password)
        self._client.connect(self.hub_adapter_host, 8883, 60)

        self._client.loop_start()

        self._terminated.wait()

    def stop(self):
        """Stop the running device."""
        if not self.is_running:
            raise ValueError("device already stopped")
        self._terminated.set()
