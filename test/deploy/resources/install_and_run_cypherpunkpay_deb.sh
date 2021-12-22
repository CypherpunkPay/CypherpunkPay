#!/bin/bash

red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

cecho () {
  echo "${green}>>> $1${reset}"
}

assert_ok () {
  if [ $? -eq 0 ]; then
    echo "OK"
    echo
  else
    echo "${red}FAILED${reset}"
    exit 1
  fi
}

verify () {
  cecho "$1"
  bash -c "$1"
  #(set -x; bash -c "$1")
  assert_ok
}

echo

# Reinstall
verify 'apt --assume-yes -qq remove cypherpunkpay || /bin/true'
verify 'apt --assume-yes install --reinstall -o Dpkg::Options::="--force-confask,confnew,confmiss" ./cypherpunkpay_1.0.3_amd64.deb'

# Waiting for the cypherpunkpay.service to start after installation
wait 6

# Show logs
# journalctl -xe --unit cypherpunkpay

# Show if service started
# systemctl status cypherpunkpay

# Run CypherpunkPay
verify 'which cypherpunkpay'
verify 'cypherpunkpay --version'
verify 'cypherpunkpay --help'

# Verify the service is running and not being restarted all the time
verify 'systemctl status cypherpunkpay.service'
wait 2
verify 'systemctl status cypherpunkpay.service'
wait 2
verify 'systemctl status cypherpunkpay.service'
wait 2
verify 'systemctl status cypherpunkpay.service'

# verify 'apt --assume-yes -qq remove cypherpunkpay || /bin/true'
# verify 'apt --assume-yes install /root/cypherpunkpay*.deb'
