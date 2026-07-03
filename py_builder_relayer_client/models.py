from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TransactionType(Enum):
    WALLET = "WALLET"
    WALLET_CREATE = "WALLET-CREATE"


@dataclass
class DepositWalletCall:
    target: str
    value: str
    data: str

    def to_dict(self):
        return {
            "target": self.target,
            "value": self.value,
            "data": self.data,
        }


@dataclass
class DepositWalletTransactionArgs:
    from_address: str
    chain_id: int
    wallet_address: str
    nonce: str
    deadline: str
    calls: list[DepositWalletCall]


@dataclass
class DepositWalletBatchRequest:
    type: str
    from_address: str
    to: str
    nonce: str
    signature: str
    deposit_wallet: str
    deadline: str
    calls: list[DepositWalletCall]

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "from": self.from_address,
            "to": self.to,
            "nonce": self.nonce,
            "signature": self.signature,
            "depositWalletParams": {
                "depositWallet": self.deposit_wallet,
                "deadline": self.deadline,
                "calls": [
                    c.to_dict() if hasattr(c, "to_dict") else c for c in self.calls
                ],
            },
        }


@dataclass
class DepositWalletCreateRequest:
    type: str
    from_address: str
    to: str

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "from": self.from_address,
            "to": self.to,
        }


class RelayerTransactionState(Enum):
    STATE_NEW = "STATE_NEW"
    STATE_EXECUTED = "STATE_EXECUTED"
    STATE_MINED = "STATE_MINED"
    STATE_INVALID = "STATE_INVALID"
    STATE_CONFIRMED = "STATE_CONFIRMED"
    STATE_FAILED = "STATE_FAILED"
