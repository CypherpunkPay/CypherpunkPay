# How to package CypherpunkPay for Debian?

## Relevant only for CypherpunkPay developers

This is internal docs for CypherpunkPay developers on how to build a DEB package.

## Steps

Have Debian or Ubuntu (this was tested on Debian).

Install build dependencies for creating *.deb out of modern python project:

```
sudo apt-get install build-essential debhelper dh-virtualenv python3-setuptools python3-pip python3-dev libffi-dev

# https://cryptography.io/en/latest/installation/#building-cryptography-on-linux
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev cargo  # cryptography package
```

Fix bug in dh-virtualenv-1.1 related to legacy usage of virtualenv:
`sudo nano /usr/lib/python2.7/dist-packages/dh_virtualenv/deployment.py`
...and comment out these two lines:
```
#            else:
#                virtualenv.append('--no-site-packages')
```

Change directory to project root:

`cd cypherpunkpay`

Setup project for development (will create local venv etc):

`bin/dev-setup`

Build deb package:
`bin/package-for-debian`

Install deb package:
`sudo dpkg -i dist/debian/cypherpunkpay_1.0.2_amd64.deb`

Verify it is installed:
`ls -lha /opt/venvs/cypherpunkpay/`

Run installed software:
`cypherpunkpay --version`

## dh_virtualenv book

https://readthedocs.org/projects/dh-virtualenv/downloads/pdf/latest/
https://github.com/spotify/dh-virtualenv

