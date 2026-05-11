from unittest import TestCase

from py_builder_relayer_client.config import get_contract_config
from py_builder_relayer_client.exceptions import RelayerClientException


class TestConfig(TestCase):
    def test_get_contract_config(self):
        for chain_id in (137, 80002):
            cfg = get_contract_config(chain_id)
            self.assertEqual(
                "0x3DaBe8f032833CE42CC26d9149660E6f596759C5",
                cfg.deposit_wallet_factory,
            )
            self.assertEqual(
                "0xFB2f5D822Ecb062dE63a7B830C5e83C994698851",
                cfg.deposit_wallet_implementation,
            )

        with self.assertRaises(RelayerClientException):
            get_contract_config(1)
