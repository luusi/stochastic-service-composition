import inspect
import multiprocessing
import os
from functools import partial
from pathlib import Path

from digital_twins.run_device import run_device

CURRENT_DIRECTORY = Path(os.path.dirname(inspect.getfile(inspect.currentframe())))

DEVICES = [
    "bathroom_heating_device",
    "bathtub_device",
    "door_device",
    "kitchen_exhaust_fan_device",
    "user_behaviour",
]

TARGET = "target"

if __name__ == "__main__":
    pool = multiprocessing.Pool(len(DEVICES) + 1)

    run_device_config = partial(run_device, path_to_json=CURRENT_DIRECTORY / ".." / "config.json")
    target_result = pool.apply_async(run_device_config, args=[TARGET], kwds=dict(is_target=True))
    results = pool.map(run_device_config, DEVICES)

    try:
        for result in results:
            result.get()
        target_result.get()
    except Exception:
        print("Interrupted.")
        pool.terminate()
