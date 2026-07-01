from unittest import TestCase

from py_builder_relayer_client.config import get_contract_config
from py_builder_relayer_client.exceptions import RelayerClientException


class TestConfig(TestCase):
    def test_get_contract_config(self):
        for chain_id in (137, 80002):
            cfg = get_contract_config(chain_id)
            self.assertEqual(
                "0x2CcdC6C5dDcd895aFcCD259F291de9b618A5cA6c",
                cfg.deposit_wallet_factory,
            )
            self.assertEqual(
                "0x74a618eBdd62Ff8579A8FE94f5B888d7623b9C35",
                cfg.deposit_wallet_beacon,
            )

        with self.assertRaises(RelayerClientException):
            get_contract_config(1)
