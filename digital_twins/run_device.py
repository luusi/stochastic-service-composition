from pathlib import Path

from digital_twins.Devices.base import BoschIotDevice
from digital_twins.Devices.utils import service_from_json
from digital_twins.things_api import config_from_json, ThingsAPI


def run_device(device_name):
    certificate_path = "digital_twins/Devices/iothub.crt"
    thing_id = f"com.bosch.services:{device_name}"

    config_path = Path("digital_twins/config.json")
    config = config_from_json(config_path)
    api = ThingsAPI(config)
    thing_service = service_from_json(api.get_thing(thing_id)[0])
    device = BoschIotDevice(device_name, thing_service, certificate_path=certificate_path)
    device.run()
