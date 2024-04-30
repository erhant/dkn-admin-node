import coincurve
from ecies.utils import generate_eth_key


def uncompressed_public_key(public_key: str) -> bytes:
    """
    Convert a compressed public key to an uncompressed public key.

    :param public_key:
    :return:
    """
    public_key_bytes = bytes.fromhex(public_key)
    public_key = coincurve.PublicKey(public_key_bytes)
    return public_key.format(compressed=False)


def generate_task_keys():
    """Generate an elliptic curve key pair.

    Returns:
        Tuple[str, str]: The private and public keys as hexadecimal strings.

    """
    eth_k = generate_eth_key()
    return eth_k.to_hex(), eth_k.public_key.to_hex()


def recover_public_key(signature, message_digest):
    """Recovers the public key from a signature and message.

    Args:
        signature (bytes): The signature from which to recover the public key. Must be exactly 65 bytes long.
        message_digest (str): Hash of the message that was signed.

    Returns:
        str: The recovered public key as a hexadecimal string, uncompressed.

    Raises:
        ValueError: If the signature is not 65 bytes long or other cryptographic errors occur.
    """

    # Ensure the message is in bytes
    if isinstance(message_digest, str):
        message_digest = message_digest.encode("utf-8")

    try:
        # Attempt to recover the public key from signature and message
        pk = coincurve.PublicKey.from_signature_and_message(signature, message_digest)
        return pk.format(compressed=True).hex()
    except Exception as e:
        raise ValueError(f"Failed to recover public key: {e}")


def sign_address(private_key, message) -> bytes:
    """Signs a message with a private key.

    Args:
        private_key (str): The private key to sign the message with.
        message (str): The message to sign.

    Returns:
        signature (bytes): The signature of the message.

    Raises:
        ValueError: If the private key is invalid or other cryptographic errors occur.

    """
    private_key_bytes = bytes.fromhex(private_key)
    private_key = coincurve.PrivateKey(private_key_bytes)

    # Ensure the message is encoded to bytes
    message_bytes = message.encode("utf-8")

    return private_key.sign_recoverable(message_bytes)


"""
{
  e: '04fc12673040ea24f29b00886d024809612515cbd6d731dec38b9fe19808c5a3c2536af20c5eed362c53eec092c102c83abaa48377429f844bdce7e20cb13e13b8f7ef6c3e0baab69bc4bb6e9c529aefd81a229aa14f349f5eec94751b05d64ec264ea06d52d80f0ed33cc9f82bf811140518a074796cb01dc1981e220',
  h: 'ebb664f25695c02af0a02d558f63d804d93317dd7a0010c01da7b0aebd433406',
  s: 'cf17731822a54890bf91757dca8cd64c0fc65ee5d857222a73a6ea0b47e1f6781cf7f8152dfb42489e2c7cd7b8009adbd9600e722fe522fbba9eba9794a25e3400'
}

signature = "410ffea37fe71725796d107cda2d6d752a8f9f8fd315f57edec18795d72f0f7b45de5c351e8632370a30c6d8263660dc988177c444acde7488aed9dcd96989ff00"
privkey = b"driadriadriadriadriadriadriadria"

priv_key = coincurve.PrivateKey(privkey)
public_key = priv_key.public_key
fpkey = public_key.format(compressed=False)
import sha3
k = sha3.keccak_256()
k.update(fpkey[1:])
address = k.digest()[-20:].hex()

result = decrypt(privkey,
                 bytes.fromhex(
                     '04dfa2ad1c86328d32d9e5d36b44e0c41d0d3e6e812a8d08de6128635e6aae171da5fcafcaa8f7971bc1c3100561038bfcb62071e961999a0c2460e63a7f829a7503df2ce8fc636efda2bd0afc6191ffc92a90d0f482c067b774d81368ce49cdc65d9e29d7ae18fc18d3388813b57e0f8e9d2f1048e49590f76a6edcf6'))

s = bytes.fromhex(
    signature)





priv_compute_node = b"dria" * 8
priv_compute_node_key = coincurve.PrivateKey(priv_compute_node)
public_compute_node = priv_compute_node_key.public_key
import hashlib

hashlib.kec

result_digest = hashlib.sha256(result).digest()
assert recover_public_key(s, result_digest) == public_compute_node.format(compressed=True).hex()

commitment_ = hashlib.sha256(s + result_digest).digest()
assert commitment_ == bytes.fromhex("f7d88c3ef604335ada2c13c7a430c21e8b8ae586c777f582cffe10fe6bcb8700")

print("a")
"""
