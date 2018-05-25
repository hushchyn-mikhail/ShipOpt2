#!/bin/bash
cd /output

cat >/tmp/runscript.sh <<EOL
#!/bin/bash
$*
EOL

chmod +x /tmp/runscript.sh

echo "skygrid: running '$*'"

/SHiPBuild/alibuild/alienv setenv FairShip/latest -w /SHiPBuild/sw -c '/tmp/runscript.sh'
