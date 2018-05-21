import time
import rrdtool
import os
from getSNMP import consultaSNMP
from aberraciones import main


def update(agente):
