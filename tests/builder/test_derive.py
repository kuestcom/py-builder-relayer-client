from unittest import TestCase

from py_builder_relayer_client.builder.derive import derive_deposit_wallet
from py_builder_relayer_client.config import get_contract_config


class TestDerive(TestCase):
    def test_derive_deposit_wallet(self):
        owner = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
        config = get_contract_config(80002)
        wallet = derive_deposit_wallet(
            owner,
            config.deposit_wallet_factory,
            config.deposit_wallet_beacon,
        )
        self.assertEqual("0xF3ab66D34F0B14C9a4f8564Ec8baaBBf51ad0Fd6", wallet)
