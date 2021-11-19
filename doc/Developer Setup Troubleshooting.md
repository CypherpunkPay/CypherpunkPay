
* **Problem:**
  The LND seconds after start gives error and shuts down:
  `[ERR] LNWL: Unable to complete chain rescan: Post "http://localhost:18332": dial tcp [::1]:18332: connect: connection`

* **Solution:**
  Unclear. It seems bitcoind itself blocked lnd from (excessive?) usage of RPC port. Maybe some connect or read timeout.
  After many attempts the problem just disappeared and lnd moved on.
