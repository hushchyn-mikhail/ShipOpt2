import ROOT
import numpy
import numpy as np
import pandas

import getopt
import sys

# For ShipGeo
from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler

# For modules
import shipDet_conf


def run_checking(input_file, geo_file, dy, reconstructiblerequired, threeprong):


    ############################################# Load SHiP geometry ###################################################

    # Check geo file
    try:
        fgeo = ROOT.TFile(geo_file)
    except:
        print "An error with opening the ship geo file."
        raise

    sGeo = fgeo.FAIRGeom

    # Prepare ShipGeo dictionary
    if not fgeo.FindKey('ShipGeo'):

        if sGeo.GetVolume('EcalModule3') :
            ecalGeoFile = "ecal_ellipse6x12m2.geo"
        else:
            ecalGeoFile = "ecal_ellipse5x10m2.geo"

        if dy:
            ShipGeo = ConfigRegistry.loadpy("$FAIRSHIP/geometry/geometry_config.py", Yheight = dy, EcalGeoFile = ecalGeoFile)
        else:
            ShipGeo = ConfigRegistry.loadpy("$FAIRSHIP/geometry/geometry_config.py", EcalGeoFile = ecalGeoFile)

    else:
        upkl    = Unpickler(fgeo)
        ShipGeo = upkl.load('ShipGeo')

    ############################################# Load SHiP modules ####################################################

    run = ROOT.FairRunSim()
    modules = shipDet_conf.configure(run,ShipGeo)

    ############################################# Load input data file #################################################

    # Check input file
    try:
        fn = ROOT.TFile(input_file,'update')
    except:
        print "An error with opening the input data file."
        raise

    sTree = fn.cbmsim

    ############################## Initialize SHiP Spectrometer Tracker geometry #######################################

    #zlayer, \
    #zlayerv2, \
    #z34layer, \
    #z34layerv2, \
    #TStation1StartZ, \
    #TStation4EndZ, \
    #VetoStationZ, \
    #VetoStationEndZ = initialize(fgeo, ShipGeo)


    ########################################## Start Checking Geometry #################################################

    all_hits = pandas.DataFrame(columns=['event_id', 'det_id', 'xtop', 'ytop', 'z', 'xbot', 'ybot'])
    all_hits_i = 0
    
    # Start event loop
    nEvents   = sTree.GetEntries()

    for iEvent in range(nEvents):

        if iEvent%100 == 0:
            print 'Event ', iEvent

        ########################################### Select one event ###################################################

        rc = sTree.GetEvent(iEvent)

        ############################################# Get hits #########################################################

        nHits = sTree.strawtubesPoint.GetEntriesFast()
        key = -1

        for i in range(nHits):

            ahit = sTree.strawtubesPoint[i]

            key+=1
            detID = ahit.GetDetectorID()
            top = ROOT.TVector3()
            bot = ROOT.TVector3()

            modules["Strawtubes"].StrawEndPoints(detID,bot,top)
            
            all_hits.loc[all_hits_i] = [iEvent, detID, top.x(), top.y(), top.z(), bot.x(), bot.y()]
            all_hits_i += 1
            
    all_hits.to_csv('hits.csv', index=False)
    all_hits['StatNb'] = all_hits['det_id'] // 10000000
    all_hits['ViewNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000) // 1000000
    all_hits['PlaneNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000) // 100000
    all_hits['LayerNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000 -\
                           all_hits['PlaneNb'] * 100000) // 10000
    all_hits['StrawNb'] = all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000 -\
                          all_hits['PlaneNb'] * 100000 - all_hits['LayerNb'] * 10000 - 2000
        
    dots00 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
             (all_hits['PlaneNb'].values==0) & (all_hits['LayerNb'].values==0)]['ytop'].values
    dots00 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
                 (all_hits['PlaneNb'].values==1) & (all_hits['LayerNb'].values==0)]['ytop'].values
    dots01 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
                 (all_hits['PlaneNb'].values==0) & (all_hits['LayerNb'].values==1)]['ytop'].values
    dots01 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
                 (all_hits['PlaneNb'].values==1) & (all_hits['LayerNb'].values==1)]['ytop'].values

    min_dist = np.hstack([np.diff(np.unique(dots00)), np.diff(np.unique(dots01)),
               np.diff(np.unique(dots00)), np.diff(np.unique(dots01))]).min()
    
    print('Pitch: ', np.round(min_dist, 3))
    
    z0 = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==0) & (all_hits['PlaneNb'].values==0) &\
                  (all_hits['LayerNb'].values==0)]['z'].mean()
    z1 = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==0) & (all_hits['PlaneNb'].values==0) &\
                  (all_hits['LayerNb'].values==1)]['z'].mean()

    print('ZShiftLayer: ', np.round(z1-z0, 3))
    
    z2 = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==0) & (all_hits['PlaneNb'].values==1) &\
                  (all_hits['LayerNb'].values==0)]['z'].mean()

    print('ZShiftPlane: ', np.round(z2-z0, 3))
    
    xtop = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==1) & (all_hits['PlaneNb']==0) &\
                    (all_hits['LayerNb']==0)]['xtop'].values[0]
    ytop = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==1) & (all_hits['PlaneNb']==0) &\
                    (all_hits['LayerNb']==0)]['ytop'].values[0]
    xbot = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==1) & (all_hits['PlaneNb']==0) &\
                    (all_hits['LayerNb']==0)]['xbot'].values[0]
    ybot = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==1) & (all_hits['PlaneNb']==0) &\
                    (all_hits['LayerNb']==0)]['ybot'].values[0]

    print('Angle: ', np.round(np.arctan((ytop - ybot) / (xtop - xbot)) * 180 / np.pi, 3))
    
    z0 = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==0) & (all_hits['PlaneNb'].values==0) &\
            (all_hits['LayerNb'].values==0)]['z'].mean()
    z3 = all_hits[(all_hits['StatNb']==1) & (all_hits['ViewNb']==1) & (all_hits['PlaneNb'].values==0) &\
            (all_hits['LayerNb'].values==0)]['z'].mean()

    print('ZShiftView: ', np.round(z3-z0, 3))
    
    dots0 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
             (all_hits['PlaneNb'].values==0) & (all_hits['LayerNb'].values==0)]['ytop'].values
    dots1 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
             (all_hits['PlaneNb'].values==0) & (all_hits['LayerNb'].values==1)]['ytop'].values

    min_dist = np.hstack([np.diff(np.unique(np.hstack([dots0, dots1])))]).min()

    print('YOffsetLayer: ', np.round(min_dist, 3))
    
    dots0 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
             (all_hits['PlaneNb'].values==0) & (all_hits['LayerNb'].values==0)]['ytop'].values
    dots1 = all_hits[(all_hits['StatNb'].values<3) & ((all_hits['ViewNb'].values==0) + (all_hits['ViewNb'].values==3)) &\
             (all_hits['PlaneNb'].values==1) & (all_hits['LayerNb'].values==0)]['ytop'].values

    min_dist = np.hstack([np.diff(np.unique(np.hstack([dots0, dots1])))]).min()

    print('YOffsetPlane: ', np.round(min_dist, 3))

    return

if __name__ == "__main__":

    input_file = None
    geo_file = None
    dy = None
    reconstructiblerequired = 2
    threeprong = 0
    model = None


    argv = sys.argv[1:]

    msg = '''Runs ship track pattern recognition.\n\
    Usage:\n\
      python RunPR.py [options] \n\
    Example: \n\
      python RunPR.py -i "ship.conical.Pythia8-TGeant4.root" -g "geofile_full.conical.Pythia8-TGeant4.root"
    Options:
      -i  --input                   : Input file path
      -g  --geo                     : Path to geo file
      -y  --dy                      : dy
      -n  --n_reco                  : NUmber of reconstructible tracks per event is required
      -t  --three                   : Is threeprong mumunu decay?
      -h  --help                    : Shows this help
      '''

    try:
        opts, args = getopt.getopt(argv, "hm:i:g:y:n:t:",
                                   ["help", "model=", "input=", "geo=", "dy=", "n_reco=", "three="])
    except getopt.GetoptError:
        print "Wrong options were used. Please, read the following help:\n"
        print msg
        sys.exit(2)
    if len(argv) == 0:
        print msg
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print msg
            sys.exit()
        elif opt in ("-m", "--model"):
            model = arg
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-g", "--geo"):
            geo_file = arg
        elif opt in ("-y", "--dy"):
            dy = float(arg)
        elif opt in ("-n", "--n_reco"):
            reconstructiblerequired = int(arg)
        elif opt in ("-t", "--three"):
            threeprong = int(arg)


    run_checking(input_file, geo_file, dy, reconstructiblerequired, threeprong)