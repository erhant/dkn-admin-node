from src.utils import uncompressed_public_key, generate_task_keys


def test_uncompressed_public_key(public_key):
    assert len(uncompressed_public_key(public_key)) == 130


def test_generate_task_keys():
    private_key, public_key = generate_task_keys()
    assert len(private_key) == 64
    assert len(public_key) == 128
