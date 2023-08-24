#!/usr/bin/env bash

INSTALLDIR="/usr/share/monitoring"
echo "To install monitoring tools root permissions are required!!"
sudo apt update
sudo apt install -y git python3-pip
sudo -H -u nagios bash -c "python3 -m pip install -U pip"
sudo -H -u nagios bash -c "python3 -m pip install wheel setuptools"
if [ -f "${INSTALLDIR}/setup.sh" ]; then
  echo "Repo exists. Updating..."
  cd ${INSTALLDIR}
  sudo git pull -f origin main
else
  sudo git clone https://github.com/artrurkovalenkotivo/monitoring.git $INSTALLDIR
fi
echo "Setup monitoring dependencies"
sudo -H -u nagios bash -c "python3 -m pip install -r ${INSTALLDIR}/requirements.txt"

echo "Scripts are copied to: ${INSTALLDIR}"
sudo chmod a+rx $INSTALLDIR/*.py
sudo chmod a+rx $INSTALLDIR/*.sh
echo "Setup succeeded"
