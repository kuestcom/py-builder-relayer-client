import logging
import time
from typing import List, Optional

from py_builder_signing_sdk.config import BuilderConfig

from .builder.derive import derive_deposit_wallet
from .builder.deposit_wallet import (
    build_deposit_wallet_batch_request,
    build_deposit_wallet_create_request,
)
from .config import get_contract_config, is_deposit_wallet_config_valid
from .endpoints import (
    GET_DEPLOYED,
    GET_NONCE,
    GET_TRANSACTION,
    GET_TRANSACTIONS,
    SUBMIT_TRANSACTION,
)
from .exceptions import RelayerClientException
from .http_helpers.helpers import get, post, POST
from .models import (
    DepositWalletCall,
    DepositWalletTransactionArgs,
    TransactionType,
)
from .response import ClientRelayerTransactionResponse
from .signer import Signer


class RelayClient:
    """
    Wallet-only client for the Kuest relayer.
    """

    def __init__(
        self,
        relayer_url,
        chain_id: int,
        private_key: str = None,
        builder_config: BuilderConfig = None,
        rpc_url: str = None,
    ):
        self.relayer_url = relayer_url[0:-1] if relayer_url.endswith("/") else relayer_url
        self.chain_id = chain_id
        self.contract_config = get_contract_config(chain_id)
        self.rpc_url = rpc_url
        self.signer = Signer(private_key, chain_id) if private_key is not None else None
        self.builder_config = builder_config
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_nonce(self, signer_address: str, signer_type: str = TransactionType.WALLET.value):
        return get(f"{self.relayer_url}{GET_NONCE}?address={signer_address}&type={signer_type}")

    def get_transaction(self, transaction_id: str):
        return get(f"{self.relayer_url}{GET_TRANSACTION}?id={transaction_id}")

    def get_transactions(self):
        return get(f"{self.relayer_url}{GET_TRANSACTIONS}")

    def get_deployed(self, address: str) -> bool:
        deployed_payload = get(f"{self.relayer_url}{GET_DEPLOYED}?address={address}")
        return bool(deployed_payload and deployed_payload.get("deployed"))

    def deploy_deposit_wallet(self):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException("Deposit Wallet contracts are not configured for this chain")

        txn_request = build_deposit_wallet_create_request(
            self.signer.address(),
            self.contract_config,
        ).to_dict()
        resp = self._post_request(POST, SUBMIT_TRANSACTION, txn_request)
        return ClientRelayerTransactionResponse(
            resp.get("transactionID"),
            resp.get("transactionHash"),
            self,
        )

    def execute_deposit_wallet_batch(
        self,
        calls: list[DepositWalletCall],
        wallet_address: str,
        deadline: str,
    ):
        self.assert_signer_needed()
        self.assert_builder_creds_needed()
        if not calls:
            raise RelayerClientException("no deposit wallet calls to execute")
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException("Deposit Wallet contracts are not configured for this chain")

        from_address = self.signer.address()
        nonce_payload = self.get_nonce(from_address, TransactionType.WALLET.value)
        if nonce_payload is None or nonce_payload.get("nonce") is None:
            raise RelayerClientException("invalid nonce payload received")

        args = DepositWalletTransactionArgs(
            from_address=from_address,
            chain_id=self.chain_id,
            wallet_address=wallet_address,
            nonce=nonce_payload.get("nonce"),
            deadline=deadline,
            calls=calls,
        )
        txn_request = build_deposit_wallet_batch_request(
            signer=self.signer,
            args=args,
            config=self.contract_config,
        ).to_dict()
        resp = self._post_request(POST, SUBMIT_TRANSACTION, txn_request)
        return ClientRelayerTransactionResponse(
            resp.get("transactionID"),
            resp.get("transactionHash"),
            self,
        )

    def derive_deposit_wallet(self):
        self.assert_signer_needed()
        if not is_deposit_wallet_config_valid(self.contract_config):
            raise RelayerClientException("Deposit Wallet contracts are not configured for this chain")
        return derive_deposit_wallet(
            self.signer.address(),
            self.contract_config.deposit_wallet_factory,
            self.contract_config.deposit_wallet_implementation,
        )

    def get_expected_deposit_wallet(self):
        return self.derive_deposit_wallet()

    def poll_until_state(
        self,
        transaction_id: str,
        states: List[str],
        fail_state: str = None,
        max_polls: Optional[int] = None,
        poll_frequency: Optional[int] = None,
    ):
        target_states = set(states)
        poll_limit = max_polls if max_polls is not None else 10
        poll_frequency_ms = poll_frequency if poll_frequency is not None and poll_frequency >= 1000 else 2000

        for _ in range(poll_limit):
            transactions = self.get_transaction(transaction_id)
            if transactions:
                txn = transactions[0]
                txn_state = txn.get("state")
                if txn_state in target_states:
                    return txn
                if fail_state is not None and txn_state == fail_state:
                    return None
            time.sleep(poll_frequency_ms / 1000)
        return None

    def _post_request(self, method: str, request_path: str, body: dict = None):
        builder_headers = self._generate_builder_headers(method, request_path, body)
        if builder_headers is None:
            raise RelayerClientException("could not generate builder headers")
        return post(f"{self.relayer_url}{request_path}", headers=builder_headers, data=body)

    def _generate_builder_headers(self, method: str, request_path: str, body: dict = None) -> Optional[dict]:
        body_for_sig = str(body) if body is not None else None
        headers = self.builder_config.generate_builder_headers(method, request_path, body_for_sig)
        return headers.to_dict() if headers is not None else None

    def assert_signer_needed(self):
        if self.signer is None:
            raise RelayerClientException("signer is required for this endpoint")

    def assert_builder_creds_needed(self):
        if self.builder_config is None:
            raise RelayerClientException("builder credentials are required for this endpoint")
