from ..robot.hexapod import Hexapod
from time import sleep

hexy =  Hexapod()

print("lie flat")
hexy.lie_flat()

print("get up")
hexy.get_up()

print("walk forward")
hexy.walk(offset = 25, swing = 25)

print("squat")
hexy.squat()

print("lie flat")
hexy.lie_flat()