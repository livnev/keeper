# Maker Keeper Framework

Reference Maker Keeper Framework.

[![Build Status](https://travis-ci.org/makerdao/keeper.svg?branch=master)](https://travis-ci.org/makerdao/keeper)
[![codecov](https://codecov.io/gh/makerdao/keeper/branch/master/graph/badge.svg)](https://codecov.io/gh/makerdao/keeper)
[![Code Climate](https://codeclimate.com/github/makerdao/keeper/badges/gpa.svg)](https://codeclimate.com/github/makerdao/keeper)
[![Issue Count](https://codeclimate.com/github/makerdao/keeper/badges/issue_count.svg)](https://codeclimate.com/github/makerdao/keeper)

## Introduction

The _SAI Stablecoin System_, as well as the _DAI Stablecoin System_ in the future,
both rely on external agents, often called _keepers_, to automate certain operations
around the Ethereum blockchain.

This project contains a set of reference keepers, which can either be run directly
by profit-seeking parties, or can be used by them as a foundation for building
their own, more sophisticated keepers.

As a part of the reference keeper implementation, an API around most of the
_SAI Stablecoin System_ contracts has been created. It can be used not only by
keepers, but may also be found useful by authors of some other, unrelated utilities
aiming to interact with these contracts.

## Disclaimer

This set of reference keepers is provided for demonstration purposes only. If you,
by any chance, want to run them on the production network or provide them
with any real money or tokens, you do it on your own responsibility only.

As stated in the _GNU Affero General Public License_:

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

## Installation

This project uses *Python 3.6.1*.

In order to install required third-party packages please execute:
```
pip install -r requirements.txt
```

### Known macOS issues

In order for the requirements to install correctly on _macOS_, please install
`openssl` and `libtool` using Homebrew:
```
brew install openssl libtool
```

and set the `LDFLAGS` environment variable before you run `pip install -r requirements.txt`:
```
export LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" 
```

## Reference keepers

This sections lists and briefly describes a set of reference keepers present in this project.

### `keeper-sai-bite`

SAI keeper to bite undercollateralized cups.

This keeper constantly looks for unsafe cups and bites them the moment they become
unsafe. Ultimately, it should take into account the profit it can make by processing
the resulting collateral via `bust` and only waste gas on `bite` if it can make it up
by subsequent arbitrage. For now, it is a dumb keeper that just bites every cup
that can be bitten.

### `keeper-sai-arbitrage`

SAI keeper to arbitrage on OasisDEX, `join`, `exit`, `boom` and `bust`.

Keeper constantly looks for profitable enough arbitrage opportunities
and executes them the moment they become available. It can make profit on:
* taking orders on OasisDEX (on SAI/SKR, SAI/W-ETH and SKR/W-ETH pairs),
* calling `join` and `exit` to exchange between W-ETH and SKR,
* calling `boom` and `bust` to exchange between SAI and SKR.

Opportunities discovered by the keeper are sequences of token exchanges
executed using methods listed above. An opportunity can consist of two
or three steps, technically it could be more but practically it will never
be more than three.

Steps can be executed sequentially (each one as a separate Etheruem
transaction, checking if one has been successful before executing the next
one) or in one ago. The latter method requires a `TxManager` contract deployed,
its address has to be passed as the `--tx-manager` argument. Also the `TxManager`
contract has to be owned by the account the keeper operates from.

You can find the source code of the `TxManager` here:
<https://github.com/reverendus/tx-manager>.

The base token of this keeper is SAI i.e. all arbitrage opportunities will
start with some amount of SAI, exchange it to some other token(s) and then exchange
back to SAI, aiming to end up with more SAI than it started with. The keeper is aware
of gas costs and takes a rough estimate of these costs while calculating arbitrage
profitability.

### `keeper-sai-top-up`

SAI keeper to top-up cups before they reach the liquidation ratio.

Kepper constantly monitors cups owned by the `--eth-from` account. If the
collateralization ratio falls under `mat` + `--min-margin`, the cup will get
topped-up up to `mat` + `--top-up-margin`.

Cups owned by other accounts are ignored.

### `keeper-sai-maker-otc`

SAI keeper to act as a market maker on OasisDEX, on the W-ETH/SAI pair.

Keeper continuously monitors and adjusts its positions in order to act as a market maker.
It aims to have open SAI sell orders for at least `--min-sai-amount` and open WETH sell
orders for at least `--min-weth-amount`, with their price in the <min-margin,max-margin>
range from the current SAI/W-ETH price.

When started, the keeper places orders for the maximum allowed amounts (`--max-sai-amount`
and `--max-weth-amount`) and uses `avg-margin` to calculate the order price.

As long as the price of existing orders is within the <min-margin,max-margin> range,
the keeper keeps them open. If they fall outside that range, they get cancelled.
If the total amount of open orders falls below either `--min-sai-amount` or
`--min-weth-amount`, a new order gets created for the remaining amount so the total
amount of orders is equal to `--max-sai-amount` / `--max-weth-amount`.

This keeper will constantly use gas to move orders as the SAI/GEM price changes,
but it can be limited by setting the margin and amount ranges wide enough.

### `keeper-sai-maker-etherdelta`

SAI keeper to act as a market maker on EtherDelta, on the ETH/SAI pair.

Due to limitations of EtherDelta, the development of this keeper has been
discontinued. It works most of the time, but due to the fact that EtherDelta
was a bit unpredictable in terms of placing orders at the time this keeper
was developed, we abandoned it and decided to stick to SaiMakerOtc for now.

## Running keepers

An individual script in the `bin` directory is present for each keeper. For example, `keeper-sai-bite`
can be run with:
```bash
bin/keeper-sai-bite --eth-from 0x0101010101010101010101010101010101010101
```

As keepers tend to die at times, in any serious environment they should be run by a tool
which can restart them if they fail. It could be _systemd_, but if you don't want to set it up,
a simple `bin/run-forever` script has been provided. Its job is to simply restart the
specified program as long as it's return code is non-zero.

For example you could run the same `keeper-sai-bite` keeper like that:
```bash
bin/run-forever bin/keeper-sai-bite --eth-from 0x0101010101010101010101010101010101010101
```
so it gets automatically restarted every time it fails.

## APIs for smart contracts

In order simplify keeper development, a set of APIs has been developed around the core contracts
of the _SAI Stablecoin_ ecosystem. The current version provides APIs around:
* `ERC20Token`,
* `Tub`, `Tap`, `Top` and `Lpc` (<https://github.com/makerdao/sai>),
* `SimpleMarket` and `ExpiringMarket` (<https://github.com/makerdao/maker-otc>),
* `TxManager` (<https://github.com/reverendus/tx-manager>),
* `DSGuard` (<https://github.com/dapphub/ds-guard>),
* `DSProxy` (<https://github.com/dapphub/ds-proxy>),
* `DSRoles` (<https://github.com/dapphub/ds-roles>),
* `DSToken` (<https://github.com/dapphub/ds-token>),
* `DSEthToken` (<https://github.com/dapphub/ds-eth-token>),
* `DSValue` (<https://github.com/dapphub/ds-value>),
* `DSVault` (<https://github.com/dapphub/ds-vault>).

In addition to that, there are draft interfaces to:
* `EtherDelta` (<https://github.com/etherdelta/etherdelta.github.io>),
* `AuctionManager` and `SplittingAuctionManager` (<https://github.com/makerdao/token-auction>).

You can find the full documentation of the APIs here: http://maker-keeper-docs.surge.sh.

**Beware!** This is the first version of the APIs and they will definitely change
and/or evolve in the future.
