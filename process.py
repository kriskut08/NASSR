import sys
import os
import subprocess

args        = sys.argv
outdir      = args[1]
mode        = args[2]
#satdump meteor_m2-x_lrpt baseband meteor_m23.f32 ./decode_1/ --samplerate 250e3 --baseband_format f32
os.system(f"satdump {mode} baseband {outdir}/recording.f32 {outdir}/decode/ --samplerate 250e3 --baseband_format f32")

# alr this is done, now I'll do something that is called a pro gamer move, and tar the entire thing
# to make downloading the raw data faster
# TODO:make this better
subprocess.Popen(["tar","-zcvf",f"{outdir}/decode.tar.gz",f"{outdir}/decode"])
