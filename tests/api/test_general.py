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

import pytest

from keeper.api import Address, Calldata
from tests.api.helpers import is_hashable


class TestAddress:
    def test_creation_from_various_representations(self):
        # expect
        assert Address('0x0000000000111111111100000000001111111111').address == \
               '0x0000000000111111111100000000001111111111'
        assert Address('0000000000111111111100000000001111111111').address == \
               '0x0000000000111111111100000000001111111111'

    def test_creation_from_another_address(self):
        # given
        some_address = Address('0x0000000000111111111100000000001111111111')

        # expect
        assert Address(some_address).address == some_address.address

    def test_should_fail_creation_from_invalid_representation(self):
        # expect
        with pytest.raises(Exception):
            Address('0x000000000011111111110000000000111111111')  # too short

        # expect
        with pytest.raises(Exception):
            Address('0x00000000001111111111000000000011111111111')  # too long

    def test_as_bytes(self):
        # expect
        assert Address('0x0000011111000001111100000111110000011111').as_bytes() == \
               b'\0\0\x01\x11\x11\0\0\x01\x11\x11\0\0\x01\x11\x11\0\0\x01\x11\x11'

    def test_string_value(self):
        # expect
        assert str(Address('0x0000011111000001111100000111110000011111')) == \
               '0x0000011111000001111100000111110000011111'

    def test_repr(self):
        # expect
        assert repr(Address('0x0000011111000001111100000111110000011111')) == \
               "Address('0x0000011111000001111100000111110000011111')"

    def test_should_be_hashable(self):
        assert is_hashable(Address('0x0000011111000001111100000111110000011111'))

    def test_equality(self):
        # given
        address1a = Address('0x0000011111000001111100000111110000011111')
        address1b = Address('0x0000011111000001111100000111110000011111')
        address2 = Address('0x0000011111000001111100000111110000022222')

        # expect
        assert address1a == address1b
        assert address1a != address2
        assert address1b != address2

    def test_ordering(self):
        # given
        address1 = Address('0x0000011111000001111100000111110000011111')
        address2 = Address('0x0000011111000001111100000111110000022222')
        address3 = Address('0x0000011111000001111100000111110000033333')

        # expect
        assert address1 < address2
        assert not address1 > address2
        assert address2 > address1
        assert not address2 < address1
        assert address1 <= address2
        assert address2 >= address1
        assert address1 < address3
        assert address1 <= address3


class TestCalldata:
    def test_creation(self):
        # expect
        assert Calldata('0xa9059cbb').value == '0xa9059cbb'

    def test_should_fail_creation_from_invalid_calldata(self):
        # expect
        with pytest.raises(Exception):
            Calldata('a9059cbb')  # without `0x`

        # expect
        with pytest.raises(Exception):
            Calldata(b'\xa9\x05\x9c\xbb')  # from bytes

    def test_as_bytes(self):
        # expect
        assert Calldata('0xa9059cbb').as_bytes() == b'\xa9\x05\x9c\xbb'

    def test_string_value(self):
        # expect
        assert str(Calldata('0xa9059cbb')) == '0xa9059cbb'

    def test_repr(self):
        # expect
        assert repr(Calldata('0xa9059cbb')) == "Calldata('0xa9059cbb')"

    def test_should_be_hashable(self):
        assert is_hashable(Calldata('0xa9059cbb'))

    def test_equality(self):
        # given
        calldata1a = Calldata('0xa9059cbb')
        calldata1b = Calldata('0xa9059cbb')
        calldata2 = Calldata('0xa9059ccc')

        # expect
        assert calldata1a == calldata1b
        assert calldata1a != calldata2
        assert calldata1b != calldata2
