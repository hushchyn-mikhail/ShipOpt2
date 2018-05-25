import subprocess
import os
import sys
import getopt
import numpy as np
import json

sys.path.append("/output/")

def objective(StrawPitch = 1.7, OffsetLayer12 = 1.76/2, OffsetPlane12 = 1.76/4, DeltazLayer = 1.1,\
              DeltazPlane = 2.6, DeltazView = 10., ViewAngle = 5, nEvents=100, method='FH'):

    ViewAngle = int(ViewAngle)
    
    FairShip = str('/SHiPBuild/sw/ubuntu1710_x86-64/FairShip/master-1/')
    with open(FairShip+'/geometry/geometry_config_original.py', 'r') as input_file,\
         open(FairShip+'/geometry/geometry_config.py', 'w') as output_file:

        for i, line in enumerate(input_file):
            
            if i == 130:
                output_file.write('    c.strawtubes.InnerStrawDiameter = 1.975*u.cm\n')
            elif i == 131:
                output_file.write('    c.strawtubes.StrawPitch         = '+str(StrawPitch)+'*u.cm\n')
            elif i == 132:
                output_file.write('    c.strawtubes.YLayerOffset       = '+str(OffsetLayer12)+'*u.cm\n')
            elif i == 133:
                output_file.write('    c.strawtubes.YPlaneOffset       = '+str(OffsetPlane12)+'*u.cm\n')
            elif i == 134:
                output_file.write('    c.strawtubes.DeltazLayer        = '+str(DeltazLayer)+'*u.cm\n')
            elif i == 135:
                output_file.write('    c.strawtubes.DeltazPlane        = '+str(DeltazPlane)+'*u.cm\n')
            elif i == 149:
                output_file.write('    c.strawtubes.ViewAngle          = '+str(ViewAngle)+'\n')
            elif i == 151:
                output_file.write('    c.strawtubes.DeltazView         = '+str(DeltazView)+'*u.cm\n')
            elif (i>=136) and (i<=143):
                output_file.write('\n')
            else:
                output_file.write(line)

    #os.chdir('/SHiPBuild/')
    #os.system('echo exit | alibuild/alienv enter FairShip/latest')
    #os.system('source /SHiPBuild/FairShipRun/config.sh')
    
    import ROOT
    from doMetrics import run_track_pattern_recognition
    
    #Run simulation
    os.chdir('/output/')
    os.system('python /SHiPBuild/FairShip/macro/run_simScript.py --caloDesign=3 --tankDesign=6 --muShieldDesign=9 --nuTauTargetDesign=3 -f /SHiPBuild/FairShip/files/Cascade-parp16-MSTP82-1-MSEL4-76Mpot_1_5000.root --nEvents '+str(nEvents))
    
    #Run reconstruction
    os.system('python /SHiPBuild/FairShip/macro/ShipReco.py -f ship.conical.Pythia8-TGeant4.root -g geofile_full.conical.Pythia8-TGeant4.root --realPR='+method)

    #Metric calculation
    input_file = '/output/ship.conical.Pythia8-TGeant4_rec.root'
    geo_file = '/output/geofile_full.conical.Pythia8-TGeant4.root'
    output_file = '/output/hists.root'

    return run_track_pattern_recognition(input_file, geo_file, output_file, method)


if __name__=='__main__':
    
    argv = sys.argv[1:]
    
    #default values for parameters
    StrawPitch = 3.6
    OffsetLayer12 = 1.9
    OffsetPlane12 = 1.3
    DeltazLayer = 1.6
    DeltazPlane = 4.2
    DeltazView = 10.
    ViewAngle = 5
    nEvents = 100
    output_file = "/output/output.txt"
    method = 'FH'
    
    try:
        opts, args = getopt.getopt(argv, "", ["pitch=", "yoffset_layer=", "yoffset_plane=", "zshift_layer=", "zshift_plane=", "zshift_view=", "alpha=", "output=", "nEvents=", "method="])
    except getopt.GetoptError:
        print("Wrong parameters. Available params: pitch, yoffset_layer, yoffset_plane, zshift_layer, zshift_plane, zshift_view, alpha, output, nEvents.\n")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == "--pitch":
            StrawPitch = arg
        elif opt == "--yoffset_layer":
            OffsetLayer12 = arg
        elif opt == "--yoffset_plane":
            OffsetPlane12 = arg
        elif opt == "--zshift_layer":
            DeltazLayer = arg
        elif opt == "--zshift_plane":
            DeltazPlane = arg
        elif opt == "--zshift_view":
            DeltazView = arg
        elif opt == "--alpha":
            ViewAngle = arg
        elif opt == "--output":
            output_file = arg
        elif opt == "--nEvents":
            nEvents = arg
        elif opt == "--method":
            method = arg
    
    with open(output_file, 'w') as tf:
        json.dump(objective(StrawPitch, OffsetLayer12, OffsetPlane12, DeltazLayer, DeltazPlane,\
                             DeltazView, ViewAngle, nEvents, method), tf)
