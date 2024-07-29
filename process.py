import sys
import os
import subprocess
import json

args            = sys.argv
dirOfTheProgram = args[1]
outdir          = args[2]
satid           = args[3]

config = json.loads(open(f"{dirOfTheProgram}/sats.json","r").read())
sats = config["sattelites"]

#satdump meteor_m2-x_lrpt baseband meteor_m23.f32 ./decode_1/ --samplerate 250e3 --baseband_format f32
os.system(f"satdump {sats[satid]["mode"]} baseband {outdir}/recording.f32 {outdir}/decode/ --samplerate 250e3 --baseband_format f32 {sats[satid]["extra_args"]}")

# alr this is done, now I'll do something that is called a pro gamer move, and tar the entire thing
# to make downloading the raw data faster
# TODO:make this better
subprocess.Popen(["tar","-zcvf",f"{outdir}/decode.tar.gz",f"{outdir}/decode"])
