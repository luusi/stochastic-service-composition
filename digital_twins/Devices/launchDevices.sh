#!/bin/bash
python2 serviceA.py & disown
python2 serviceB.py & disown
python2 serviceC.py & disown
python2 serviceD.py & disown
python2 serviceE.py & disown
