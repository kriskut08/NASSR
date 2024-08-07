import os
import sys

outdir =          sys.argv[1] # the output directory
freq =            sys.argv[2] # the frequency
tarnsDur =        sys.argv[3] # transit duration
dirOfTheProgram = sys.argv[4] # this explains itself...
satid           = sys.argv[5]
#os.system('satdump live {i["mode"]} {outdir} --source rtlsdr --samplerate 2.4e6 --frequency {i["frequency"]} --lna_agc --gain 37 --timeout {str(transit.duration())} --http_server 127.0.0.1:8998')
print(f'satdump record {outdir}/recording --source rtlsdr --samplerate 250e3 --frequency {freq}e6 --gain 45 --baseband_format f32 --timeout {tarnsDur} --agc')
os.system(f'satdump record {outdir}/recording --source rtlsdr --samplerate 250e3 --frequency {freq}e6 --gain 45 --baseband_format f32 --timeout {tarnsDur} --agc')

# the reason I'm separating the two stages, is because I'd like to have some way to re-decode 
# a recrding if idk like meteor m2-4 broadcasts something where the rs check fails anyway this is 
# TODO:this :D
# btw idk why I'm writing this down because noone will see this RIGHT?

os.system(f'python3 {dirOfTheProgram}/process.py {dirOfTheProgram} {outdir} {satid}')
