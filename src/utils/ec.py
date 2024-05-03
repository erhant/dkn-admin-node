import logging
from typing import Tuple

import coincurve
from ecies.utils import generate_eth_key

logger = logging.getLogger(__name__)


def uncompressed_public_key(public_key: str) -> bytes:
    """
    Convert a compressed public key to an uncompressed public key.

    :param public_key: The compressed public key as a hexadecimal string.
    :return: The uncompressed public key as bytes.

    Raises:
        ValueError: If the provided public key is invalid.
    """
    try:
        public_key_bytes = bytes.fromhex(public_key)
        public_key = coincurve.PublicKey(public_key_bytes)
        return public_key.format(compressed=False)
    except Exception as e:
        logger.error(f"Error converting public key: {e}", exc_info=True)
        raise ValueError(f"Failed to convert public key: {e}") from e


def generate_task_keys() -> Tuple[str, str]:
    """
    Generate an elliptic curve key pair.

    Returns:
        Tuple[str, str]: The private and public keys as hexadecimal strings.
    """
    try:
        eth_k = generate_eth_key()
        return eth_k.to_hex(), eth_k.public_key.to_hex()
    except Exception as e:
        logger.error(f"Error generating task keys: {e}", exc_info=True)
        raise e


def recover_public_key(signature: bytes, message_digest: str) -> str:
    """
    Recovers the public key from a signature and message.

    Args:
        signature (bytes): The signature from which to recover the public key. Must be exactly 65 bytes long.
        message_digest (str): Hash of the message that was signed.

    Returns:
        str: The recovered public key as a hexadecimal string, compressed.

    Raises:
        ValueError: If the signature is not 65 bytes long or other cryptographic errors occur.
    """
    try:
        # Ensure the message is in bytes
        if isinstance(message_digest, str):
            message_digest = message_digest.encode("utf-8")

        # Attempt to recover the public key from signature and message
        pk = coincurve.PublicKey.from_signature_and_message(signature, message_digest)
        return pk.format(compressed=True).hex()
    except Exception as e:
        logger.error(f"Error recovering public key: {e}", exc_info=True)
        raise ValueError(f"Failed to recover public key: {e}") from e


def sign_address(private_key: str, message: str) -> bytes:
    """
    Signs a message with a private key.

    Args:
        private_key (str): The private key to sign the message with.
        message (str): The message to sign.

    Returns:
        bytes: The signature of the message.

    Raises:
        ValueError: If the private key is invalid or other cryptographic errors occur.
    """
    try:
        private_key_bytes = bytes.fromhex(private_key)
        private_key = coincurve.PrivateKey(private_key_bytes)

        # Ensure the message is encoded to bytes
        message_bytes = message.encode("utf-8")

        return private_key.sign_recoverable(message_bytes)
    except Exception as e:
        logger.error(f"Error signing address: {e}", exc_info=True)
        raise ValueError(f"Failed to sign address: {e}") from e
