import ROOT
import numpy
import numpy as np
import pandas

import getopt
import sys
import os

from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler

from mctruth import getReconstructibleTracks

import shipDet_conf

from geo_init import initialize


def dmetric(input_file, geo_file, dy, reconstructiblerequired, threeprong):

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

    zlayer, \
    zlayerv2, \
    z34layer, \
    z34layerv2, \
    TStation1StartZ, \
    TStation4EndZ, \
    VetoStationZ, \
    VetoStationEndZ = initialize(ShipGeo)


    ########################################## Start Checking Geometry #################################################

    all_hits = pandas.DataFrame(columns=['event_id', 'det_id', 'track_id', 'xtop', 'ytop', 'z', 'xbot', 'ybot'])
    all_hits_i = 0
    
    # Start event loop
    nEvents   = sTree.GetEntries()

    for iEvent in range(nEvents):

        if iEvent%100 == 0:
            print 'Event ', iEvent

        ########################################### Select one event ###################################################

        rc = sTree.GetEvent(iEvent)

        ############################################# Get hits #########################################################
        
        reco_mc_tracks = getReconstructibleTracks(iEvent,
                                                  sTree,
                                                  sGeo,
                                                  reconstructiblerequired,
                                                  threeprong,
                                                  TStation1StartZ,
                                                  TStation4EndZ,
                                                  VetoStationZ,
                                                  VetoStationEndZ)
        
        #consider only reconstructible events
        if len(reco_mc_tracks) > 1:

            nHits = sTree.strawtubesPoint.GetEntriesFast()
            key = -1

            for i in range(nHits):

                ahit = sTree.strawtubesPoint[i]

                key+=1
                detID = ahit.GetDetectorID()
                trID = ahit.GetTrackID()
                top = ROOT.TVector3()
                bot = ROOT.TVector3()

                modules["Strawtubes"].StrawEndPoints(detID,bot,top)

                all_hits.loc[all_hits_i] = [iEvent, detID, trID, top.x(), top.y(), top.z(), bot.x(), bot.y()]
                all_hits_i += 1
            
    all_hits['StatNb'] = all_hits['det_id'] // 10000000
    all_hits['ViewNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000) // 1000000
    all_hits['PlaneNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000) // 100000
    all_hits['LayerNb'] = (all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000 -\
                           all_hits['PlaneNb'] * 100000) // 10000
    all_hits['StrawNb'] = all_hits['det_id'] - all_hits['StatNb'] * 10000000 - all_hits['ViewNb'] * 1000000 -\
                          all_hits['PlaneNb'] * 100000 - all_hits['LayerNb'] * 10000 - 2000
    
    #save dataframe with hits
    #ShipOpt = str(os.getenv('SHIPOPT'))
    #all_hits.to_csv(ShipOpt+'/temp/hits.csv', index=False)
    
    #return daniel's metric
    df_1_view = all_hits[(all_hits.StatNb==1)&(all_hits.ViewNb==0)]
    counts = df_1_view.groupby(['event_id', 'track_id'])['StatNb'].count()
    
    return 1. * np.sum(counts>1) / len(counts)