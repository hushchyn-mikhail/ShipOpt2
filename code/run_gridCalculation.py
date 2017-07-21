import numpy as np
import pandas as pd
import os
import sys

from objective import objective

ShipOpt = str(os.getenv('SHIPOPT'))

if 'initial_design.npy' in os.listdir(ShipOpt+'/observations/'):
    initial_design = np.load(ShipOpt+'/observations/initial_design.npy')
else:
    print('''
          There are no file "initial_design.npy" at directory "$SHIPOPT/observations/".
          Try to generate it using command: "python gridGenerator.py"
          ''')
    sys.exit()

if 'observations.csv' in os.listdir(ShipOpt+'/observations/'):
    observations = pd.read_csv(ShipOpt+'/observations/observations.csv')
else:
    observations = pd.DataFrame(columns=['num', 'pitch', 'yoffset_layer', 'yoffset_plane', 'zshift_layer',\
                                         'zshift_plane', 'zshift_view', 'angle', 'objective'])

for point in initial_design:
    
    try:
        value = objective(*tuple(point))
    except:
        value = None

    observations.loc[len(observations)] = [len(observations)]+list(point)+[value]
    observations.to_csv(ShipOpt+'/observations/observations.csv', index=False)