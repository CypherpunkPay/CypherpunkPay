# CypherpunkPay

CypherpunkPay is a modern **self-hosted** software for accepting Bitcoin donations or Bitcoin payments as a merchant.

Being a single, **self-contained Linux daemon**, it is uniquely easy to install, with no dependencies, near-zero configuration and low hardware requirements.

See the [official website](https://cypherpunkpay.org/) ([Tor onion](http://cypay73v4kp3i74splu2hv4yuruwhyzq4fxalyvmb76mrsgiwlaq7mqd.onion/)).

## Docs for donations and merchants

All docs are available on the [official website](https://cypherpunkpay.org/) ([Tor onion](http://cypay73v4kp3i74splu2hv4yuruwhyzq4fxalyvmb76mrsgiwlaq7mqd.onion/)).

## Docs for contributors

### Prerequisites for development

* Linux
* Python 3.7.3+

### Developer setup

After cloning this repo, review and run:

`bin/dev-setup`

This will update pip, install poetry and then use poetry to install dependencies.

### Running app in dev env

To run the app in development environment, start the server:

`bin/dev-server`

...then go to http://127.0.0.1:6543/

Admin panel:
http://127.0.0.1:6543/cypherpunkpay/admin/eeec6kyl2rqhys72b6encxxrte/

Dummy store:
http://127.0.0.1:6543/cypherpunkpay/dummystore/

### Running tests

To run the unit tests:

`bin/test-unit`

To run the full test suite you need **unpruned and synced-up bitcoind running on testnet** with default settings.
Then:

`bin/test`

The database for tests is separate from development and gets reset on each test run.

### Resetting dev database

Just remove database file:

`rm /tmp/cypherpunkpay-dev.sqlite3`

## Public domain

CypherpunkPay is "dual-licensed" under **Unlicense** OR **MIT**.
The Unlicense attempts to explicitly put CypherpunkPay in the public domain,
while MIT is an alternative or fallback if you want it for legal reasons.

SPDX-License-Identifier: Unlicense OR MIT
