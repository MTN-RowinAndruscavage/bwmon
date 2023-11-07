import json

sdata={}
sdata['microphone']=""
sdata['motion']=""  # 
#sdata['light']=""   # lux (no driver)
sdata['temperature']=""  # celsius
sdata['humidity']=""   # percent

def jsondump():
    jsondat = json.dumps(sdata)
    return jsondat