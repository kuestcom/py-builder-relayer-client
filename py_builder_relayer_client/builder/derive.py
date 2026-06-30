from eth_abi import encode
from eth_utils import to_bytes, to_checksum_address, keccak

ERC1967_BEACON_CONST1 = "0x60195155f3363d3d373d3d363d602036600436635c60da"
ERC1967_BEACON_CONST2 = "0x1b60e01b36527fa3f0ad74e5423aebfd80d3ef4346578335a9a72aeaee59ff6c"
ERC1967_BEACON_CONST3 = "0xb3582b35133d50545afa5036515af43d6000803e604d573d6000fd5b3d6000f3"
ERC1967_BEACON_PREFIX = 0x6100523D8160233D3973


def get_create2_address(bytecode_hash: str, from_address: str, salt: bytes) -> str:
    bytecode_hash = bytecode_hash[2:] if bytecode_hash.startswith("0x") else bytecode_hash
    from_address = from_address[2:] if from_address.startswith("0x") else from_address
    address_hash = keccak(
        b"\xff"
        + to_bytes(hexstr=from_address)
        + salt
        + to_bytes(hexstr=bytecode_hash)
    )
    return to_checksum_address(address_hash[-20:].hex())


def init_code_hash_erc1967_beacon_proxy(beacon: str, args: bytes) -> str:
    beacon = to_checksum_address(beacon)
    n = len(args)
    combined = ERC1967_BEACON_PREFIX + (n << 56)
    init_code = (
        combined.to_bytes(10, "big")
        + to_bytes(hexstr=beacon)
        + to_bytes(hexstr=ERC1967_BEACON_CONST1)
        + to_bytes(hexstr=ERC1967_BEACON_CONST2)
        + to_bytes(hexstr=ERC1967_BEACON_CONST3)
        + args
    )
    return "0x" + keccak(init_code).hex()


def derive_deposit_wallet(owner: str, factory: str, beacon: str) -> str:
    owner = to_checksum_address(owner)
    factory = to_checksum_address(factory)
    beacon = to_checksum_address(beacon)

    wallet_id = to_bytes(hexstr=owner).rjust(32, b"\x00")
    args = encode(["address", "bytes32"], [factory, wallet_id])
    salt = keccak(args)
    bytecode_hash = init_code_hash_erc1967_beacon_proxy(beacon, args)
    return get_create2_address(bytecode_hash=bytecode_hash, from_address=factory, salt=salt)
