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


#this is needed because this makes it possible to check for overlap
#IMPORTANT note for overlap checking: it priorotizes based on the position in the sats.json
scheduled = []


for i in range(len(sats)):
    tle= sats[i]["tle"]

    sat = predict.observe(tle, qth)
    print(sat['name'])

    prediction = predict.transits(tle,qth,int(datetime.now().timestamp()),int(datetime.now().timestamp())+86400) # +one day
    #print("Start of Transit\tTransit Duration (s)\tPeak Elevation")
    for transit in prediction:
        #overlap checking and min elevation checking
        #thank you random stackoverflow user for the idea ;) https://stackoverflow.com/a/25369187
        overlap=False
        for j in scheduled:
            #two passes overlap when the firts ones start and the second ones end is less than the sum of the two passes duration
            maxdur = max(j[1],transit.end) - min(j[0],transit.start)
            if maxdur < j[2] + int(transit.duration()):
                overlap = True
        
        above_min_elev = float(transit.peak()['elevation']) > min_peak_elev 

        if not(overlap) and above_min_elev:
            # ok this is the part where we schedule jobs 
            # NOTE: this is extremely shit and I do not like it but here we go :'D
            print("scheduling...")
            scheduled.append([transit.start,transit.end,int(transit.duration())])
            outdir = "/satdata/"+str(sat["name"]).lower().replace(" ","_")+"_"+ str(datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%y%b%-d-%H:%M'))
            time = datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%-Y%m%d%H%M.%S') #this is for at
            pwd = os.popen("pwd").read()[:-1] # kell a :-1 mert a process outputon van egy \n
            print(f'python3 {pwd}/record.py {outdir} {sats[i]["frequency"]} {str(int(transit.duration()))} {pwd} {i}')

            os.system(f'echo "python3 {pwd}/record.py {outdir} {sats[i]["frequency"]} {str(int(transit.duration()))} {pwd} {i}" | at -t {time}')
        else:
            print("OVERLAP DETECTED or NOT ABOVE MINIMUM PEAK ELEVATION, not scheduling")
        
print(len(scheduled))