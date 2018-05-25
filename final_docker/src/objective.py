Last login: Fri Mar 30 21:24:50 on ttys001
MacBook-Pro-Oleg:~ oleg$ ssh oalenkin@lxplus.cern.ch
Warning: Permanently added the RSA host key for IP address '137.138.152.22' to the list of known hosts.
Password: 
* ********************************************************************
* Welcome to lxplus084.cern.ch, SLC, 6.9
* Archive of news is available in /etc/motd-archive
* Reminder: You have agreed to comply with the CERN computing rules
* https://cern.ch/ComputingRules
* Puppet environment: production, Roger state: production
* Foreman hostgroup: lxplus/nodes/login
* Availability zone: cern-geneva-a
* LXPLUS Public Login Service - https://cern.ch/lxplusdoc
* ********************************************************************
********************************************************************************
*                         ---- LHCb Login v9r2p4 ----                          *
*      Building with gcc62 on slc6 x86_64 system (x86_64-slc6-gcc62-opt)       *
********************************************************************************
 --- User_release_area is set to /afs/cern.ch/user/o/oalenkin/cmtuser
 --- LHCBPROJECTPATH is set to:
    /cvmfs/lhcb.cern.ch/lib/lhcb
    /cvmfs/lhcb.cern.ch/lib/lcg/releases
    /cvmfs/lhcb.cern.ch/lib/lcg/app/releases
    /cvmfs/lhcb.cern.ch/lib/lcg/external
--------------------------------------------------------------------------------
[oalenkin@lxplus084 ~]$ final
Welcome to Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-109-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  Get cloud support with Ubuntu Advantage Cloud Guest:
    http://www.ubuntu.com/business/services/cloud

104 packages can be updated.
0 updates are security updates.


*** System restart required ***
Last login: Fri Mar 30 17:16:11 2018 from 137.138.76.165
**************************************************************************
# A new feature in cloud-init identified possible datasources for        #
# this system as:                                                        #
#   ['Ec2', 'None']                                                      #
# However, the datasource used was: OpenStack                            #
#                                                                        #
# In the future, cloud-init will only attempt to use datasources that    #
# are identified or specifically configured.                             #
# For more information see                                               #
#   https://bugs.launchpad.net/bugs/1669675                              #
#                                                                        #
# If you are seeing this message, please file a bug against              #
# cloud-init at                                                          #
#    https://bugs.launchpad.net/cloud-init/+filebug?field.tags=dsid      #
# Make sure to include the cloud provider your instance is               #
# running on.                                                            #
#                                                                        #
# After you have filed a bug, you can disable this warning by launching  #
# your instance with the cloud-config below, or putting that content     #
# into /etc/cloud/cloud.cfg.d/99-warnings.cfg                            #
#                                                                        #
# #cloud-config                                                          #
# warnings:                                                              #
#   dsid_missing_source: off                                             #
**************************************************************************

Disable the warnings above by:
  touch /home/ubuntu/.cloud-warnings.skip
or
  touch /var/lib/cloud/instance/warnings/.skip
ubuntu@final:~$ ls
anaconda3  devel  final_docker  new_docker  oliver_docker  ShipOpt2  src  test
ubuntu@final:~$ docker ps -a
CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS               NAMES
ubuntu@final:~$ docker run -it oleg94/ship_metric:latest /bin/bash
root@3bf80e7f9264:/# cd /opt
root@3bf80e7f9264:/opt# ls
disney-run.sh  doMetrics.py  objective.py
root@3bf80e7f9264:/opt# vi objective.py 

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
-- INSERT --                                                                                                                            51,118        46%

