from dataclasses import dataclass
from eth_utils import to_checksum_address

from .exceptions import RelayerClientException


@dataclass
class ContractConfig:
    deposit_wallet_factory: str
    deposit_wallet_beacon: str


DEPOSIT_WALLET_FACTORY = to_checksum_address(
    "0x2CcdC6C5dDcd895aFcCD259F291de9b618A5cA6c"
)
DEPOSIT_WALLET_BEACON = to_checksum_address(
    "0x74a618eBdd62Ff8579A8FE94f5B888d7623b9C35"
)

CONFIG = {
    137: ContractConfig(
        deposit_wallet_factory=DEPOSIT_WALLET_FACTORY,
        deposit_wallet_beacon=DEPOSIT_WALLET_BEACON,
    ),
    80002: ContractConfig(
        deposit_wallet_factory=DEPOSIT_WALLET_FACTORY,
        deposit_wallet_beacon=DEPOSIT_WALLET_BEACON,
    ),
}


def get_contract_config(chain_id: int) -> ContractConfig:
    config = CONFIG.get(chain_id)
    if config is None:
        raise RelayerClientException(f"Invalid chainID: {chain_id}")
    return config


def is_deposit_wallet_config_valid(config: ContractConfig) -> bool:
    return bool(config.deposit_wallet_factory) and bool(config.deposit_wallet_beacon)
