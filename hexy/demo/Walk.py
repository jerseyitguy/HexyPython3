from ..robot.hexapod import Hexapod
from time import sleep

hexy =  Hexapod()

print("lie flat")
hexy.lie_flat()

print("walk forward")
hexy.walk(offset = 25, swing = 25)

print("lie flat")
hexy.lie_flat()