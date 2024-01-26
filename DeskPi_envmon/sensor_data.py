import json
import array
import os

# Rolling tally of motion events per minute
class BinaryArray:
    def __init__(self):
        self.array = array.array('B', [0] * 60)
        self.index = 0

    def insert(self, value):
        self.array[self.index] = value
        self.index = (self.index + 1) % 60

    def sum(self):
        return sum(self.array)

def sys_df():
    # Returns [kiB] (total, used, available)
    stats = os.statvfs('/')
    bsize = stats[0]  # 512 on the Pico W
    tot_blocks = stats[2]
    free_blocks = stats[3]
    used_blocks = tot_blocks - free_blocks

    return (tot_blocks * bsize / 1024, used_blocks * bsize / 1024, free_blocks * bsize / 1024)

sdata={}
sdata['microphone']=""
sdata['motion']=""  # motion sensor (True/False)
sdata['motion_per_minute']=BinaryArray()
#sdata['light']=""   # lux (no driver)
sdata['temperature']=""  # celsius
sdata['humidity']=""   # percent

def jsondump():
    tempdata = sdata.copy()
    tempdata['motion_per_minute'] = sdata['motion_per_minute'].sum()
    return json.dumps(tempdata)
