# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2017 reverendus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pprint import pformat
from typing import Optional, List

from web3 import Web3

from api import Contract, Address, Receipt, Calldata, Transact
from api.numeric import Wad
from api.token import ERC20Token
from api.util import int_to_bytes32, bytes_to_int


class OfferInfo:
    """Represents a single offer on `SimpleMarket` (`OasisDEX`).

    Attributes:
        offer_id: Id of the offer.
        sell_how_much: The amount of the `sell_which_token` token which is put on sale.
        sell_which_token: The address of the token which is put on sale.
        buy_how_much: The price the offer creator wants to be paid, denominated in the `buy_which_token` token.
        buy_which_token: The address of the token the offer creator wants to be paid with.
        owner: Ethereum address of the owner of this offer.
        timestamp: Date and time when this offer has been created, as a unix timestamp.
    """

    def __init__(self, offer_id: int, sell_how_much: Wad, sell_which_token: Address, buy_how_much: Wad,
                 buy_which_token: Address, owner: Address, timestamp: int):
        self.offer_id = offer_id
        self.sell_how_much = sell_how_much
        self.sell_which_token = sell_which_token
        self.buy_how_much = buy_how_much
        self.buy_which_token = buy_which_token
        self.owner = owner
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.offer_id == other.offer_id

    def __repr__(self):
        return pformat(vars(self))


class LogMake:
    def __init__(self, args):
        self.id = bytes_to_int(args['id'])
        self.maker = Address(args['maker'])
        self.have_token = Address(args['haveToken'])
        self.have_amount = Wad(args['haveAmount'])
        self.want_token = Address(args['wantToken'])
        self.want_amount = Wad(args['wantAmount'])
        self.timestamp = args['timestamp']

    def __repr__(self):
        return pformat(vars(self))


class LogBump:
    def __init__(self, args):
        self.id = bytes_to_int(args['id'])
        self.maker = Address(args['maker'])
        self.have_token = Address(args['haveToken'])
        self.have_amount = Wad(args['haveAmount'])
        self.want_token = Address(args['wantToken'])
        self.want_amount = Wad(args['wantAmount'])
        self.timestamp = args['timestamp']

    def __repr__(self):
        return pformat(vars(self))


class LogTake:
    def __init__(self, args):
        self.id = bytes_to_int(args['id'])
        self.maker = Address(args['maker'])
        self.taker = Address(args['taker'])
        self.have_token = Address(args['haveToken'])
        self.take_amount = Wad(args['takeAmount'])
        self.want_token = Address(args['wantToken'])
        self.give_amount = Wad(args['giveAmount'])
        self.timestamp = args['timestamp']

    def __repr__(self):
        return pformat(vars(self))


class LogKill:
    def __init__(self, args):
        self.id = bytes_to_int(args['id'])
        self.maker = Address(args['maker'])
        self.have_token = Address(args['haveToken'])
        self.have_amount = Wad(args['haveAmount'])
        self.want_token = Address(args['wantToken'])
        self.want_amount = Wad(args['wantAmount'])
        self.timestamp = args['timestamp']

    def __repr__(self):
        return pformat(vars(self))


class SimpleMarket(Contract):
    """A client for a `SimpleMarket` contract.

    `SimpleMarket` is a simple on-chain OTC market for ERC20-compatible tokens.
    It powers the `OasisDEX` decentralized exchange.

    You can also interact with `ExpiringMarket` contracts, as their API is
    identical to `SimpleMarket`.

    You can find the source code of the `SimpleMarket` contract here:
    <https://github.com/makerdao/maker-otc>.

    Attributes:
        web3: An instance of `Web` from `web3.py`.
        address: Ethereum address of the `SimpleMarket` contract.
    """

    abi = Contract._load_abi(__name__, 'abi/SimpleMarket.abi')
    bin = Contract._load_bin(__name__, 'abi/SimpleMarket.bin')

    def __init__(self, web3: Web3, address: Address):
        self.web3 = web3
        self.address = address
        self._assert_contract_exists(web3, address)
        self._contract = web3.eth.contract(abi=self.abi)(address=address.address)
        self._none_offers = set()

    @staticmethod
    def deploy(web3: Web3):
        """Deploy a new instance of the `SimpleMarket` contract.

        Args:
            web3: An instance of `Web` from `web3.py`.

        Returns:
            A `SimpleMarket` class instance.
        """
        return SimpleMarket(web3=web3, address=Contract._deploy(web3, SimpleMarket.abi, SimpleMarket.bin, []))

    def approve(self, tokens: List[ERC20Token], approval_function):
        for token in tokens:
            approval_function(token, self.address, 'OasisDEX')

    def on_make(self, handler):
        self._on_event(self._contract, 'LogMake', LogMake, handler)

    def on_bump(self, handler):
        self._on_event(self._contract, 'LogBump', LogBump, handler)

    def on_take(self, handler):
        self._on_event(self._contract, 'LogTake', LogTake, handler)

    def on_kill(self, handler):
        self._on_event(self._contract, 'LogKill', LogKill, handler)

    def past_make(self, number_of_past_blocks: int) -> List[LogMake]:
        return self._past_events(self._contract, 'LogMake', LogMake, number_of_past_blocks)

    def past_bump(self, number_of_past_blocks: int) -> List[LogBump]:
        return self._past_events(self._contract, 'LogBump', LogBump, number_of_past_blocks)

    def past_take(self, number_of_past_blocks: int) -> List[LogTake]:
        return self._past_events(self._contract, 'LogTake', LogTake, number_of_past_blocks)

    def past_kill(self, number_of_past_blocks: int) -> List[LogKill]:
        return self._past_events(self._contract, 'LogKill', LogKill, number_of_past_blocks)

    def get_last_offer_id(self) -> int:
        """Get the id of the last offer created on the market.

        Returns:
            The id of the last offer. Returns `0` if no offers have been created at all.
        """
        return self._contract.call().last_offer_id()

    def get_offer(self, offer_id: int) -> Optional[OfferInfo]:
        """Get the offer details.

        Args:
            offer_id: The id of the offer to get the details of.

        Returns:
            An instance of `OfferInfo` if the offer is still active, or `None` if the offer has been
            already completely taken.
        """

        # if an offer is None, it won't become not-None again for the same OTC instance
        if offer_id in self._none_offers:
            return None

        array = self._contract.call().offers(offer_id)
        if array[5] is not True:
            self._none_offers.add(offer_id)
            return None
        else:
            return OfferInfo(offer_id=offer_id,
                             sell_how_much=Wad(array[0]),
                             sell_which_token=Address(array[1]),
                             buy_how_much=Wad(array[2]),
                             buy_which_token=Address(array[3]),
                             owner=Address(array[4]),
                             timestamp=array[6])

    def active_offers(self) -> List[OfferInfo]:
        offers = [self.get_offer(offer_id + 1) for offer_id in range(self.get_last_offer_id())]
        return [offer for offer in offers if offer is not None]

    #TODO make it return the id of the newly created offer
    def make(self, have_token: Address, have_amount: Wad, want_token: Address, want_amount: Wad) -> Transact:
        """Create a new offer.

        The `have_amount` of `have_token` token will be taken from you on offer creation and deposited
        in the market contract. Allowance needs to be set first. Refer to the `approve()` method
        in the `ERC20Token` class.

        Args:
            have_token: Address of the ERC20 token you want to put on sale.
            have_amount: Amount of the `have_token` token you want to put on sale.
            want_token: Address of the ERC20 token you want to be paid with.
            want_amount: Amount of the `want_token` you want to receive.

        Returns:
            A `Transact` instance, which can be used to trigger the transaction.
        """
        return Transact(self, self.web3, self.abi, self.address, self._contract,
                        'make', [have_token.address, want_token.address, have_amount.value, want_amount.value])

    def take(self, offer_id: int, quantity: Wad) -> Optional[Receipt]:
        """Takes (buys) an offer.

        If `quantity` is equal to `sell_how_much`, the whole offer will be taken (bought) which will make it
        disappear from the order book. If you want to buy a fraction of the offer, set `quantity` to a number
        lower than `sell_how_much`.

        Args:
            offer_id: Id of the offer you want to take (buy).
            quantity: Quantity of `sell_which_token` that you want to buy.

        Returns:
            A `Receipt` if the Ethereum transaction was successful and the offer has been taken (bought).
            `None` if the Ethereum transaction failed.
        """
        return self._transact(self.web3, f"SimpleMarket('{self.address}').take('{offer_id}', '{quantity}')",
                              lambda: self._contract.transact().take(int_to_bytes32(offer_id), quantity.value))

    def take_calldata(self, offer_id: int, quantity: Wad) -> Calldata:
        return Calldata(self.web3.eth.contract(abi=self.abi).encodeABI('take', [int_to_bytes32(offer_id), quantity.value]))

    def kill(self, offer_id: int) -> Transact:
        """Cancels an existing offer.

        Offers can be cancelled only by their owners. In addition to that, in case of expiring markets,
        after the market has expired all orders can be cancelled by anyone.

        Args:
            offer_id: Id of the offer you want to cancel.

        Returns:
            A `Transact` instance, which can be used to trigger the transaction.
        """
        return Transact(self, self.web3, self.abi, self.address, self._contract, 'kill', [int_to_bytes32(offer_id)])

    def __repr__(self):
        return f"SimpleMarket('{self.address}')"
