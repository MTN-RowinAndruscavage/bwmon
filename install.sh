#!/bin/bash

# For ubuntu clients
# Rowin.Andruscavage1@T-Mobile.com   2023-09-26

if [[ -x /snap/bin/firefox ]]; then
  echo "Firefox installed from snap doesn't work with selenium in Ubuntu 22.04 + XWayland"
  echo "Install the APT package of Firefox per:"
  echo "https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04"
  exit 1
fi

sudo apt update; sudo apt install -y jq apcalc curl monitoring-plugins \
                      atop iftop glances

# Install pyenv
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
# sudo curl https://pyenv.run | bash
# # TODO: Set up .bashrc

# Install slack/msteams notification script
pushd notify
python3 -m pip install -U pipenv
pipenv install
popd

# Install Speedtest
sudo apt install -y speedtest | grep newest \
|| curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt install -y speedtest

# Install check-mk agent
sudo apt show check-mk-agent | grep "2.2.0p10" \
|| sudo dpkg -i check-mk-agent_2.2.0p10-1_all.deb


FILES=(
    check_icmp.sh
    # mtr.py  # traceroute is a bit derpy on lab network
    speedtest_agent_plugin.sh
    speedtest_failed.json
)

for F in ${FILES[@]} ; do
    sudo cp $F /usr/lib/check_mk_agent/plugins/
    sudo chmod 755 /usr/lib/check_mk_agent/plugins/${F}
done

sudo rm /usr/lib/check_mk_agent/plugins/mtr.py

sudo chmod 644 /usr/lib/check_mk_agent/plugins/speedtest_failed.json
sudo cp mtr.cfg /etc/check_mk/


NOTIFICATIONS=(
  slack
  msteams
)

for NOTIFICATION in ${NOTIFICATIONS[@]} ; do
  sudo cp notify/speedtest_2_${NOTIFICATION}.service /etc/systemd/system/
  sudo systemctl status speedtest_2_${NOTIFICATION} \
	|| sudo systemctl enable speedtest_2_${NOTIFICATION} \
	; sudo systemctl start speedtest_2_${NOTIFICATION}
done

echo "
sudo cmk-agent-ctl register -i te5ghub -s 192.168.0.2 -U cmkadmin --trust-cert --hostname $HOSTNAME
"
