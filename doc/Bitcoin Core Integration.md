# Bitcoin Core Integration - CypherpunkPay Developer Docs

This is internal docs on how CypherpunkPay code interacts with Bitcoin Core.

## Assumptions

* **Do** support the pruned mode. This implies txindex=0 because txindex is incompatible with pruning.

* **Do not** require 3rd party indexing service on top of Bitcoin Core (no Electrum Server or NBXplorer). Few moving parts.

* Use modern wallet definition using output descriptors.

## Background Knowledge

Output descriptors specs:
https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md

xpub/tpub specs (Extended Public Key):
https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki#serialization-format

zpub/vpub specs (Extended Public Key with implied derivation path):
https://github.com/satoshilabs/slips/blob/master/slip-0132.md

## Bitcoin Core RPC API Docs

Bitcoin Core RPC calls relevant for CypherpunkPay payment processing:

https://developer.bitcoin.org/reference/rpc/getblockcount.html          - tip height
https://developer.bitcoin.org/reference/rpc/getblockchaininfo.html      - tip height, tip hash, if pruned, etc

https://developer.bitcoin.org/reference/rpc/listwallets.html            - check if wallet exists
https://developer.bitcoin.org/reference/rpc/createwallet.html           - create watch only wallet (keyless skeleton)
https://developer.bitcoin.org/reference/rpc/getdescriptorinfo.html      - get descriptor checksum
https://developer.bitcoin.org/reference/rpc/importdescriptors.html      - import descriptor to make wallet functional
https://developer.bitcoin.org/reference/rpc/getreceivedbyaddress.html   - received total amount but without details

This would be ideal but `listreceivedbyaddress` does not work with pruned/descriptor wallets:
https://developer.bitcoin.org/reference/rpc/listreceivedbyaddress.html  - get transactions received by specific address (IDs only)
https://developer.bitcoin.org/reference/rpc/gettransaction.html         - get transaction details

Other interesting calls that are probably useless for us:
https://developer.bitcoin.org/reference/rpc/scantxoutset.html           - only unspent outputs - could lead to bugs when immediately spent
https://developer.bitcoin.org/reference/rpc/loadwallet.html             - load watch only wallet after Bitcoin Core restart (not necessary if autoload enabled)

## Generating throw away wallets

https://iancoleman.io/bip39/

## Converting xpub <--> zpub and tpub <--> vpub

https://jlopp.github.io/xpub-converter/
https://www.reddit.com/r/Bitcoin/comments/he8max/how_is_an_xpub_converted_to_a_ypubzpub/

`electrum convert_xkey 'xpub...' 'p2wpkh'`

For Bitcoin Core API calls:
* zpub needs to be converted to xpub
* vpub needs to be converted to tpub

## Example Bitcoin Core RPC API calls

### List wallets

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
    "method": "listwallets"
  }''' \
  --header 'content-type: text/plain;' http://127.0.0.1:18332
```

=> error (bitcoind not ready)
```Bash
{"result":null,"error":{"code":-28,"message":"Loading block index..."},"id":null}
```

=> success (empty list)
```Bash
{"result":[],"error":null,"id":null}
```

=> success (exists)
```Bash
{"result":["wallet-cypherpunkpay-3"],"error":null,"id":null}
```

### Create empty wallet (no keys)

```Bash

# wallet_name, disable_private_keys=true, blank=true, passphrase=null, avoid_reuse=false, descriptors=true, load_on_startup=true

curl --user 'bitcoin:secret' --data-binary '''
  {
    "method": "createwallet",
    "params": ["wallet-cypherpunkpay-3", true, true, null, false, true, true]
  }''' \
  --header 'content-type: text/plain;' http://127.0.0.1:18332/
```

=> error (already exists)
```Bash
{"result":null,"error":{"code":-4,"message":"Wallet file verification failed. Failed to create database path '/var/lib/bitcoind-testnet/testnet3/wallet-cypherpunkpay-3'. Database already exists."},"id":null}
```

=> success
```Bash
{"result":{"name":"wallet-cypherpunkpay-3","warning":"Wallet is an experimental descriptor wallet"},"error":null,"id":null}
```

### Load existing wallet (not necessary with load_on_startup=true)

```
curl --user 'bitcoin:secret' --data-binary '''
  {
    "method": "loadwallet",
    "params": ["wallet-cypherpunkpay-3", true]
  }'''   --header 'content-type: text/plain;' http://127.0.0.1:18332
```

=> error (Path does not exist)
```Bash
{"result":null,"error":{"code":-18,"message":"Wallet file verification failed. Failed to load database path '/var/lib/bitcoind-testnet/testnet3/removeme7'. Path does not exist."},"id":null}
```

=> error (being used by another bitcoind)
```Bash
{"result":null,"error":{"code":-4,"message":"Wallet file verification failed. SQLiteDatabase: Unable to obtain an exclusive lock on the database, is it being used by another bitcoind?\n"},"id":null}
```

### Get descriptor checksum for further calls

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "getdescriptorinfo",
      "params": ["wpkh([00000000/84h/1h/0h]tpub.../0/*)"]
  }''' \
  --header 'Content-Type: text/plain;' localhost:18332
```

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "getdescriptorinfo",
      "params": ["wpkh(tpub/0/*)"]
  }''' \
  --header 'Content-Type: text/plain;' localhost:18332
```

=> error (invalid key)
```Bash
{"result":null,"error":{"code":-5,"message":"key 'tpub...' is not valid"},"id":null}
```

=> success
```Bash
{"result":{"descriptor":"wpkh([00000000/84'/1'/0']tpub.../0/*)#w9netwcy","checksum":"a5vx3508","isrange":true,"issolvable":true,"hasprivatekeys":false},"error":null,"id":null}
```

### Is node pruned?

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
    "method": "getblockchaininfo"
  }''' \
  --header 'content-type: text/plain;' http://127.0.0.1:18332
```


### Import xpub/tpub to establish actual watch-only wallet

if pruned:
  timestamp = utc_now() - 2.5 days  # fit default 550MB pruned mainnet
else:
  timestamp = utc_now() - 90 days   # we give up to 90 days to recognize confirmations

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "importdescriptors",
      "params":
          {
              "requests":
                [
                  {
                    "desc": "wpkh(tpub.../0/*)#fgqlfv5p",
                    "timestamp": 1618451329,
                    "watchonly": true,
                    "internal": false,
                    "active": true,
                    "range": [0, 1000]
                  }
                ]
          }
  }''' \
  --header 'Content-Type: text/plain;' localhost:18332/wallet/wallet-cypherpunkpay-3
```

=> error

```Bash
{"result":[{"success":false,"error":{"code":-1,"message":"Rescan failed for descriptor with timestamp 1608451329. There was an error reading a block from time 1610045558, which is after or within 7200 seconds of key creation, and could contain transactions pertaining to the desc. As a result, transactions and coins using this desc may not appear in the wallet. This error could be caused by pruning or data corruption (see bitcoind log for details) and could be dealt with by downloading and rescanning the relevant blocks (see -reindex and -rescan options)."}}],"error":null,"id":null}
```

=> success

```Bash
{"result":[{"success":true}],"error":null,"id":null}
```

### Get transactions received by address (IDs only)

Does NOT work with pruned node so currently useless for us.

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "listreceivedbyaddress",
      "params": [0, true, true, "tb1qwgvj90v6h6lde0lyec4utgtk223xx6qdgxh8lv"]
  }''' \
  --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-3
```

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "listreceivedbyaddress",
      "params": [0, true, true, "tb1q25umfw6rwtumnj7dyhrzcztkfqu64kqn49eluh"]
  }''' \
  --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-3
```

=> success (empty)

```Bash
{"result":[],"error":null,"id":"curltest"}
```

=> success (existing)

### Get total amount received by address

**This** is the key API call that CypherpunkPay leverages:

* it does work with pruned nodes for recent balances (within the last 550 blocks or ~3.5 days with default `prune=550`)
* it is not affected by spends from the address which is exactly what we need (merchant spending the funds shouldn't affect payment recognition)

The unfortunate limitation is that response does not contain number of confirmations (if any).
To learn about confirmations, we call it multiple times, while incrementing `minconf` parameter.
This way we incrementally learn what amount has how many confirmations.

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "getreceivedbyaddress",
      "params": ["tb1qwgvj90v6h6lde0lyec4utgtk223xx6qdgxh8lv", 0]
  }''' \
  --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-3
```


## Other messy examples

### Example `scantxoutset` usage (mainnet)

This is not currently used by CypherpunkPay but remains an interesting option.

```Bash
time curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "scantxoutset",
      "params":
      {
          "action": "start",
          "scanobjects":
          [
              "addr(bc1qga8zs4suxj50tu6wfz2w3dpt2r0jh46lfzqjs7)",
              "addr(bc1q4s2auk8hjakg3z2akr9vmg2ht6u873tj2jvqts)",
              "addr(348EFy6MaxLFyY1b6DzHjX6YEHb7Mvgd1f)",
              "addr(bc1qwrnxaqezw0zrmlxefq3hfhcq37vkaq0zjem2j3)",
              "addr(bc1qvupupywrlwfp6av9ylzwc7h3e7epc3jl95c8cj)"
          ]
      }
  }''' \
  --header 'Content-Type: text/plain;' localhost:8332
```

### Get wallet info

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "getwalletinfo",
      "params": []
  }''' \
  --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-3
```


### List (all) transactions

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "listtransactions",
      "params": ["*", 0, 100]
  }''' \
  --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-2
```


### List unspent

```Bash
curl --user 'bitcoin:secret' --data-binary '''
  {
      "method": "listunspent",
      "params": [0, 9999999, ["tb1q..."]]
  }'''   --header 'Content-Type: text/plain;' http://127.0.0.1:18332/wallet/wallet-cypherpunkpay-2
```
