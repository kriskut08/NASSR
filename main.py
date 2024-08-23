
# Made by kriskut08
# 
#_____   ______________________________ 
#___  | / /__    |_  ___/_  ___/__  __ \
#__   |/ /__  /| |____ \_____ \__  /_/ /
#_  /|  / _  ___ |___/ /____/ /_  _, _/ 
#/_/ |_/  /_/  |_/____/ /____/ /_/ |_|  
#                                       

from datetime import datetime
import tzlocal
import json
import predict
import os



def strListToTuple(string:str):
    list = string.split(",")
    retlist = []
    for i in list:
        retlist.append(float(i))
    return tuple(retlist)


#tle = """METEOR M2-4
#1 59051U 24039A   24119.18467111  .00000161  00000-0  91960-4 0  9991
#2 59051  98.5939  82.3205 0005866 270.9284  89.1222 14.22217075  8386"""

config = open("sats.json","r").read()

print(config)
cnfg_json = json.loads(config)
#                E longtitude to west :D
#qth = (47.188200,360-18.408900,110)
qth = strListToTuple(cnfg_json["qth"])
print(qth)
local_timezone = tzlocal.get_localzone()

sats = cnfg_json["sattelites"]

os.system("for i in `atq | awk '{print $1}'`;do atrm $i;done")

min_peak_elev = int(cnfg_json["minimum_elevation"])


scheduled = []


for i in range(len(sats)):
    tle= sats[i]["tle"]

    sat = predict.observe(tle, qth)
    print(sat['name'])

    prediction = predict.transits(tle,qth,int(datetime.now().timestamp()),int(datetime.now().timestamp())+86400) # +one day
    #print("Start of Transit\tTransit Duration (s)\tPeak Elevation")
    for transit in prediction:
        #elevation checking
        above_min_elev = float(transit.peak()['elevation']) > min_peak_elev 
        if above_min_elev:
            #overlap checking
            #thank you random stackoverflow user for the idea ;) https://stackoverflow.com/a/25369187
            overlapnum=None
            overlap=False
            for j in range(len(scheduled)):
                #two passes overlap when the firts ones start and the second ones end is less than the sum of the two passes duration
                maxdur = max(scheduled[j][1],transit.end) - min(scheduled[j][0],transit.start)
                if maxdur < scheduled[j][2] + int(transit.duration()):
                    overlap = True
                    overlapnum = j

            if not(overlap):
                #this happens when there is no overlap so we can just add it to the schedule :D
                # NOTE: this is extremely shit and I do not like it but here we go :'D
                print("No overlap, adding to schedule list...")
                outdir = "/satdata/"+str(sat["name"]).lower().replace(" ","_")+"_"+ str(datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%y%b%-d-%H:%M'))
                time = datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%-Y%m%d%H%M.%S') #this is for at
                pwd = os.popen("pwd").read()[:-1] # kell a :-1 mert a process outputon van egy \n
                print(f'python3 {pwd}/record.py {outdir} {sats[i]["frequency"]} {str(int(transit.duration()))} {pwd} {i}')
                #add to list
                scheduled.append([transit.start,transit.end,int(transit.duration()),float(transit.peak()['elevation']),f'echo "python3 {pwd}/record.py {outdir} {sats[i]["frequency"]} {str(int(transit.duration()))} {pwd} {i}" | at -t {time}'])
            else:
                #overlap is detected
                print("OVERLAP DETECTED")
                overlapedMaxElavation = scheduled[overlapnum][3]
                # this is probably not the prettiest way but this is the best i could come up with
                if overlapedMaxElavation < float(transit.peak()['elevation']): #check if the transit is higher than the one it overlaps with
                    print("Newer pass has higher peak elevation, overwriting! -------------------------------------------------")
                    # this is repeated code
                    outdir = "/satdata/"+str(sat["name"]).lower().replace(" ","_")+"_"+ str(datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%y%b%-d-%H:%M'))
                    time = datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%-Y%m%d%H%M.%S') #this is for at
                    pwd = os.popen("pwd").read()[:-1] # the :-1 is needed because the process output has a \n on its end
                    print("old:")
                    print(scheduled[overlapnum])
                    scheduled[overlapnum] = [transit.start,transit.end,int(transit.duration()),float(transit.peak()['elevation']),f'echo "python3 {pwd}/record.py {outdir} {sats[i]["frequency"]} {str(int(transit.duration()))} {pwd} {i}" | at -t {time}']
                    print("new:")
                    print(scheduled[overlapnum])

print("""
#----------------------
# scheduling with at...
#----------------------""")
for i in scheduled:
    os.system(i[4])
    print("-"*15)
    print(f"transit start:{str(i[0])}, end:{str(i[1])}, duration: {str(i[2])}, peak: {str(i[3])}, cmd: '{i[4]}'")
print(scheduled)