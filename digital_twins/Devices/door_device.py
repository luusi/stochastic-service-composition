import logging

from digital_twins.run_device import run_device

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    run_device("door_device")
