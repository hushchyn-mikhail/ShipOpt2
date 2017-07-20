import numpy as np
import pandas as pd
import os
import sys

from objective import objective

if 'initial_design.npy' in os.listdir('../observations/'):
    initial_design = np.load('../observations/initial_design.npy')
else:
    print('''
          There are no file "initial_design.npy" at directory "../observations".
          Try to generate it using command: "python2 gridGenerator.py"
          ''')
    sys.exit()

if 'observations.csv' in os.listdir('../observations/'):
    observations = pd.read_csv('../observations/observations.csv')
else:
    observations = pd.DataFrame(columns=['num', 'pitch', 'yoffset_layer', 'yoffset_plane', 'zshift_layer',\
                                         'zshift_plane', 'zshift_view', 'angle', 'objective'])

for point in initial_design:
    
    value = objective(*tuple(point))
    observations.loc[len(observations)] = [len(observations)]+list(point)+[value]
    observations.to_csv('../observations/observations.csv', index=False)