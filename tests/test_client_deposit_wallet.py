from unittest import TestCase
from unittest.mock import Mock, patch

from py_builder_relayer_client.client import RelayClient
from py_builder_relayer_client.http_helpers.helpers import POST
from py_builder_relayer_client.models import DepositWalletCall, TransactionType
from py_builder_relayer_client.endpoints import SUBMIT_TRANSACTION


# Public Hardhat/Anvil fixture key. This is not a live credential.
TEST_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
WALLET = "0x053258Cfb6124a089363F89dA04b2eFa39b34e2d"
TOKEN = "0x0000000000000000000000000000000000000001"
APPROVE_CALLDATA = "0x095ea7b30000000000000000000000000000000000000000000000000000000000000002ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"


class TestClientDepositWallet(TestCase):

    def _client(self):
        client = RelayClient(
            relayer_url="http://localhost:8080",
            chain_id=137,
            private_key=TEST_PRIVATE_KEY,
            builder_config=object(),
        )
        client._post_request = Mock(
            return_value={"transactionID": "test-txn", "transactionHash": "0xabc"}
        )
        client.get_nonce = Mock(return_value={"nonce": "0"})
        return client

    def test_get_expected_deposit_wallet(self):
        client = self._client()
        self.assertEqual(WALLET, client.get_expected_deposit_wallet())

    def test_get_deployed(self):
        client = self._client()
        with patch(
            "py_builder_relayer_client.client.get", return_value={"deployed": True}
        ) as mock_get:
            self.assertTrue(client.get_deployed(WALLET))

        mock_get.assert_called_once_with(f"http://localhost:8080/deployed?address={WALLET}")

    def test_get_transactions_matches_upstream_no_builder_auth(self):
        client = self._client()
        builder_config = Mock()
        client.builder_config = builder_config

        with patch("py_builder_relayer_client.client.get", return_value=[]) as mock_get:
            self.assertEqual([], client.get_transactions())

        mock_get.assert_called_once_with("http://localhost:8080/transactions")
        builder_config.generate_builder_headers.assert_not_called()

    def test_deploy_deposit_wallet_posts_wallet_create(self):
        client = self._client()
        resp = client.deploy_deposit_wallet()

        expected_body = {
            "type": TransactionType.WALLET_CREATE.value,
            "from": ADDRESS,
            "to": client.contract_config.deposit_wallet_factory,
        }
        client._post_request.assert_called_once_with(
            POST, SUBMIT_TRANSACTION, expected_body
        )
        self.assertEqual("test-txn", resp.transaction_id)
        self.assertEqual("0xabc", resp.transaction_hash)

    def test_generate_builder_headers_matches_upstream_dict_body_signing(self):
        client = self._client()
        headers = Mock()
        headers.to_dict.return_value = {"KUEST_BUILDER_SIGNATURE": "sig"}
        builder_config = Mock()
        builder_config.generate_builder_headers.return_value = headers
        client.builder_config = builder_config

        body = {
            "type": TransactionType.WALLET_CREATE.value,
            "from": ADDRESS,
            "to": client.contract_config.deposit_wallet_factory,
        }

        self.assertEqual(
            {"KUEST_BUILDER_SIGNATURE": "sig"},
            client._generate_builder_headers(POST, SUBMIT_TRANSACTION, body),
        )
        builder_config.generate_builder_headers.assert_called_once_with(
            POST,
            SUBMIT_TRANSACTION,
            str(body),
        )

    def test_execute_deposit_wallet_batch_posts_wallet_request(self):
        client = self._client()
        call = DepositWalletCall(target=TOKEN, value="0", data=APPROVE_CALLDATA)
        resp = client.execute_deposit_wallet_batch(
            calls=[call],
            wallet_address=WALLET,
            deadline="1234567890",
        )

        method, path, body = client._post_request.call_args[0]
        self.assertEqual(POST, method)
        self.assertEqual(SUBMIT_TRANSACTION, path)
        self.assertEqual(TransactionType.WALLET.value, body["type"])
        self.assertEqual(ADDRESS, body["from"])
        self.assertEqual(client.contract_config.deposit_wallet_factory, body["to"])
        self.assertEqual("0", body["nonce"])
        self.assertTrue(body["signature"].startswith("0x"))
        self.assertEqual(132, len(body["signature"]))
        self.assertEqual(
            {
                "depositWallet": WALLET,
                "deadline": "1234567890",
                "calls": [call.to_dict()],
            },
            body["depositWalletParams"],
        )
        self.assertEqual("test-txn", resp.transaction_id)
