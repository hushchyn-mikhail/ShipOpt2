import subprocess
import os
import ROOT
import numpy as np
from daniel import dmetric

def objective(StrawPitch = 1.7, OffsetLayer12 = 1.76/2, OffsetPlane12 = 1.76/4, DeltazLayer = 1.1,\
              DeltazPlane = 2.6, DeltazView = 10., ViewAngle = 5):

    ViewAngle = int(ViewAngle)
    
    FairShip = str(os.getenv('FAIRSHIP'))
    with open(FairShip+'/geometry/geometry_config_original.py', 'r') as input_file,\
         open(FairShip+'/geometry/geometry_config.py', 'w') as output_file:

        for i, line in enumerate(input_file):
            if i == 129:
                output_file.write('    c.strawtubes.StrawPitch         = '+str(StrawPitch)+'*u.cm\n')
            elif i == 130:
                output_file.write('    c.strawtubes.OffsetLayer12      = '+str(OffsetLayer12)+'*u.cm\n')
            elif i == 131:
                output_file.write('    c.strawtubes.OffsetPlane12      = '+str(OffsetPlane12)+'*u.cm\n')
            elif i == 132:
                output_file.write('    c.strawtubes.DeltazLayer        = '+str(DeltazLayer)+'*u.cm\n')
            elif i == 133:
                output_file.write('    c.strawtubes.DeltazPlane        = '+str(DeltazPlane)+'*u.cm\n')
            elif i == 136:
                output_file.write('    c.strawtubes.ViewAngle          = '+str(ViewAngle)+'\n')
            elif i == 138:
                output_file.write('    c.strawtubes.DeltazView         = '+str(DeltazView)+'*u.cm\n')
            else:
                output_file.write(line)

    #Run simulation
    ShipOpt = str(os.getenv('SHIPOPT'))
    os.chdir(ShipOpt+'/temp/')
    os.system('python $FAIRSHIP/macro/run_simScript.py')

    #Metric calculation
    input_file = 'ship.conical.Pythia8-TGeant4.root'
    geo_file = 'geofile_full.conical.Pythia8-TGeant4.root'
    dy = None
    reconstructiblerequired = 2
    threeprong = 0

    return dmetric(input_file, geo_file, dy, reconstructiblerequired, threeprong)