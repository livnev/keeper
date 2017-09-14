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

from keeper.api import Address, Wad
from keeper.api.approval import directly
from keeper.api.token import DSToken
from web3 import EthereumTesterProvider
from web3 import Web3

from keeper.api.etherdelta import EtherDelta


class TestEtherDelta:
    def setup_method(self):
        self.web3 = Web3(EthereumTesterProvider())
        self.web3.eth.defaultAccount = self.web3.eth.accounts[0]
        self.our_address = Address(self.web3.eth.defaultAccount)
        self.etherdelta = EtherDelta.deploy(self.web3,
                                            admin=Address('0x1111100000999998888877777666665555544444'),
                                            fee_account=Address('0x8888877777666665555544444111110000099999'),
                                            account_levels_addr=Address('0x6666655555444441111188888777770000099999'),
                                            fee_make=Wad.from_number(0.01),
                                            fee_take=Wad.from_number(0.02),
                                            fee_rebate=Wad.from_number(0.03),
                                            api_server='http://none.invalid')
        self.token1 = DSToken.deploy(self.web3, 'AAA')
        self.token1.mint(Wad.from_number(100)).transact()

    def test_addresses(self):
        # expect
        assert self.etherdelta.admin() == Address('0x1111100000999998888877777666665555544444')
        assert self.etherdelta.fee_account() == Address('0x8888877777666665555544444111110000099999')
        assert self.etherdelta.account_levels_addr() == Address('0x6666655555444441111188888777770000099999')

    def test_fees(self):
        # expect
        assert self.etherdelta.fee_make() == Wad.from_number(0.01)
        assert self.etherdelta.fee_take() == Wad.from_number(0.02)
        assert self.etherdelta.fee_rebate() == Wad.from_number(0.03)

    def test_deposit_and_withdraw_eth(self):
        # when
        self.etherdelta.deposit(Wad.from_number(2.5)).transact()

        # then
        assert self.etherdelta.balance_of(self.our_address) == Wad.from_number(2.5)

        # when
        self.etherdelta.withdraw(Wad.from_number(1.1)).transact()

        # then
        assert self.etherdelta.balance_of(self.our_address) == Wad.from_number(1.4)

    def test_deposit_and_withdraw_token(self):
        # given
        self.etherdelta.approve([self.token1], directly())

        # when
        self.etherdelta.deposit_token(self.token1.address, Wad.from_number(1.5)).transact()

        # then
        assert self.etherdelta.balance_of_token(self.token1.address, self.our_address) == Wad.from_number(1.5)

        # when
        self.etherdelta.withdraw_token(self.token1.address, Wad.from_number(0.2)).transact()

        # then
        assert self.etherdelta.balance_of_token(self.token1.address, self.our_address) == Wad.from_number(1.3)

    def test_should_have_printable_representation(self):
        assert repr(self.etherdelta) == f"EtherDelta('{self.etherdelta.address}')"
