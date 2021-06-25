# CypherpunkPay

CypherpunkPay is a modern **self-hosted** software for accepting Bitcoin donations or Bitcoin payments as a merchant.

Being a single, **self-contained Linux daemon**, it is uniquely easy to install, with no dependencies, near-zero configuration and low hardware requirements.

See the [official website](https://cypherpunkpay.org/) ([Tor onion](http://cypay73v4kp3i74splu2hv4yuruwhyzq4fxalyvmb76mrsgiwlaq7mqd.onion/)).

## Docs for donations and merchants

All docs are available on the [official website](https://cypherpunkpay.org/) ([Tor onion](http://cypay73v4kp3i74splu2hv4yuruwhyzq4fxalyvmb76mrsgiwlaq7mqd.onion/)).

## Docs for contributors

Development prerequisites:

* Linux
* Python 3.7.3+

After cloning this repo, review and run:

`bin/dev-setup`

To run the app in development environment:

`bin/dev-server`

To run the unit tests:

`bin/test-unit`

To run the full tests you need unpruned and synced-up bitcoind running on testnet with default settings. Then:

`bin/test`


## Public domain

CypherpunkPay is "dual-licensed" under Unlicense OR MIT.
The Unlicense attempts to explicitly put CypherpunkPay in the public domain,
while MIT is an alternative or fallback if you want it for legal reasons.

SPDX-License-Identifier: Unlicense OR MIT
