from dataclasses import dataclass
from eth_utils import to_checksum_address

from .exceptions import RelayerClientException


@dataclass
class ContractConfig:
    deposit_wallet_factory: str
    deposit_wallet_implementation: str


DEPOSIT_WALLET_FACTORY = to_checksum_address("0x3DaBe8f032833CE42CC26d9149660E6f596759C5")
DEPOSIT_WALLET_IMPLEMENTATION = to_checksum_address("0xFB2f5D822Ecb062dE63a7B830C5e83C994698851")

CONFIG = {
    137: ContractConfig(
        deposit_wallet_factory=DEPOSIT_WALLET_FACTORY,
        deposit_wallet_implementation=DEPOSIT_WALLET_IMPLEMENTATION,
    ),
    80002: ContractConfig(
        deposit_wallet_factory=DEPOSIT_WALLET_FACTORY,
        deposit_wallet_implementation=DEPOSIT_WALLET_IMPLEMENTATION,
    ),
}


def get_contract_config(chain_id: int) -> ContractConfig:
    config = CONFIG.get(chain_id)
    if config is None:
        raise RelayerClientException(f"Invalid chainID: {chain_id}")
    return config


def is_deposit_wallet_config_valid(config: ContractConfig) -> bool:
    return bool(config.deposit_wallet_factory) and bool(config.deposit_wallet_implementation)
