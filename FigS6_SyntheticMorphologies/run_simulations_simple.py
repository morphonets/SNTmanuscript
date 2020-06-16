
import random
import subprocess
import os
import os.path
import glob

t_growth = 6
max_random_seed = 100000000
num_grns = 5
num_neurons = 1000

working_directory = os.path.expanduser('~/IJ/Neuroanatomy-Unstable/Fiji.app')
os.chdir(working_directory)

cmd_list = ['./ImageJ-linux64', '--headless','--run', 'sc.iview.cx3d.commands.GRNBranchingSWC']
cmd = ' '.join(cmd_list)
#cmd = 'timeout 100s ./ImageJ-linux64 --run sc.iview.cx3d.commands.GRNBranchingSWC "'

params = {}
params['maxTime'] = t_growth
params['randomSeed'] = 2208191
params['filenameSWC'] = "test.swc"
params['filenameGRN'] = "test.grn"
params['filenameStats'] = "cx3dStats.csv"
params['generateGRN'] = False
params['sciViewEnabled'] = "false"

def filenameFromParams( params ):
    filename = 'snt'
    for k in ['maxTime', 'filenameGRN', 'randomSeed']:
        filename += '_' + k + '_' + str(params[k])
    return filename + '.swc'

random.seed(239823474981)

# find remaining experiments
# run until no experiments remain
#
# or easier:
# find all experiments
# check if output swc exists, if so, then skip

grn_count = 0
while grn_count < num_grns:

    params['generateGRN'] = False

    print(['grn_count', grn_count])

    neuron_count = 0
    while neuron_count <= num_neurons:
        rs = random.randint(0,max_random_seed)
        tg = t_growth

        print(['neuron_count', neuron_count])

        if neuron_count == 0:
            params['generateGRN'] = "false"
        else:
            params['generateGRN'] = "false"
        params['randomSeed'] = rs
        params['maxTime'] = tg
        params['filenameGRN'] = 'grn_%d.grn' % ( grn_count )
        params['filenameSWC'] = filenameFromParams(params)
        params['filenameStats'] = 'grn_%d.csv' % ( grn_count )

        arglist = []
        for k in params.keys():
            if k == 'filenameSWC' or k == 'filenameStats' or k == 'filenameGRN':
                arglist += [k + '="' + str(params[k]) + '"']
            else:
                arglist += [k + '=' + str(params[k])]
        argstr = ','.join(arglist)

        needs_more_neurons = True
        if os.path.exists(params['filenameStats']) and neuron_count == 0:

            stats = []
            with open(params['filenameStats']) as f:
                stats = f.readlines()

            needs_more_neurons = (len(stats) < neuron_count + 1)
            neuron_count = len(stats)

            swc_list = glob.glob('*' + params['filenameGRN'] + '*.swc')

            neuron_count = len(swc_list)

            print(['Found precomputed neurons: ',neuron_count,swc_list[:3]])

        if (not os.path.exists(params['filenameSWC'])) and needs_more_neurons:

            #sp_call = cmd_list[:-1]+[cmd_list[-1]+ " '" + argstr + "'" ]
            sp_call = cmd_list+[ "'" + argstr + "'" ]
            sp_call = ' '.join(sp_call)

            print(sp_call)

            try:
                out = subprocess.check_output(sp_call, shell=True, timeout=100)
                print(out)
            except:
                print('Exception, probably timeout')

        neuron_count += 1
    grn_count += 1
