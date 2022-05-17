
How to use address and private view key to verify TXO ownership:
https://medium.com/@philipshen13/monero-part-2-how-it-works-983a6344bd58
https://medium.com/@philipshen13/monero-part-1-key-concepts-3671186016c6
https://www.getmonero.org/library/Zero-to-Monero-2-0-0.pdf

https://monero.stackexchange.com/questions/746/is-there-an-online-block-explorer-that-supports-view-keys

Block explorers - mainnet:
* https://xmrchain.net/
* https://melo.tools/explorer/mainnet/
* https://monero.exan.tech/
* https://xmrblocks.bisq.services/
* https://www.exploremonero.com/deposit
* https://monerohash.com/explorer/
* https://blox.minexmr.com/

Block explorers - stagenet:
* https://melo.tools/explorer/stagenet/
* DOWN https://stagenet.xmrchain.net/
* DOWN https://monero-stagenet.exan.tech

Charge payment recognition algorithm (draft):

* For each charge recently activated (7 days or younger):
  * For each transaction in mempool and with timestamp *after* charge.activated_at
    * For each TXO (transaction output)
      * Verify if belongs to charge.cc_address
