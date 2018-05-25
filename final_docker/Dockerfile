from scr4t/ship:16.01.2018-disney

RUN ls

RUN cd SHiPBuild/FairShip && git pull

RUN cd SHiPBuild && alibuild/aliBuild build --defaults fairship -c shipdist FairShip

RUN cp /SHiPBuild/FairShip/geometry/geometry_config.py /SHiPBuild/FairShip/geometry/geometry_config_original.py; mkdir /output

RUN pip install scikit-learn

RUN apt-get install -y vim

COPY src/* /opt/

RUN cp /SHiPBuild/sw/ubuntu1710_x86-64/FairShip/master-1/geometry/geometry_config.py /SHiPBuild/sw/ubuntu1710_x86-64/FairShip/master-1/geometry/geometry_config_original.py 

RUN cp /opt/shipStrawTracking.py /SHiPBuild/FairShip/python/; chmod +x /opt/disney-run.sh

RUN mv /opt/shipStrawTracking.py /SHiPBuild/sw/ubuntu1710_x86-64/FairShip/master-1/python/
