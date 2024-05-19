from  datetime import datetime
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
#config = "\n".join(config.split(r"\n"))
print(config)
cnfg_json = json.loads(config)
#                E longtitude to west :D
#qth = (47.188200,360-18.408900,110)
qth = strListToTuple(cnfg_json["qth"])
print(qth)
local_timezone = tzlocal.get_localzone()

sats = cnfg_json["sattelites"]

os.system("for i in `atq | awk '{print $1}'`;do atrm $i;done")
for i in sats:
    tle= i["tle"]

    sat = predict.observe(tle, qth)
    print(sat['name'])

    prediction = predict.transits(tle,qth,int(datetime.now().timestamp()),int(datetime.now().timestamp())+86400) # +one day
    print("Start of Transit\tTransit Duration (s)\tPeak Elevation")
    for transit in prediction:
        print(f"{transit.start}\t{transit.duration()}\t{transit.peak()['elevation']}")
        # ok this is the part where we schedule jobs 
        # NOTE: this is extremely shit and I do not like it but here we go :'D
        print("scheduling...")
        outdir = "/satdata/"+str(sat["name"]).lower().replace(" ","_")+"_"+ str(datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%y%b%-d-%H:%M'))
        time = datetime.fromtimestamp(float(transit.start), local_timezone).strftime('%-Y%m%d%H%M.%S') #this is for at and it is the LEAST sane mode of specifying time. 
        # like look at this shit:  YYMMDDhhmm.ss
        print(f'echo "satdump live {i["mode"]} {outdir} --source rtlsdr --samplerate 2.4MSPS --frequency {i["frequency"]} --lna_agc --gain 37 --timeout {str(transit.duration())} --http_server 127.0.0.1:8998" | at -t {time}')
        os.system(f'echo "satdump live {i["mode"]} {outdir} --source rtlsdr --samplerate 2.4MSPS --frequency {i["frequency"]} --lna_agc --gain 37 --timeout {str(transit.duration())} --http_server 127.0.0.1:8998" | at -t {time}')