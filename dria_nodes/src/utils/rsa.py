import rsa


def generate_keys():
    # Generate public and private keys
    (public_key, private_key) = rsa.newkeys(512)  # Using 512 bits for demonstration purposes

    # Convert the public and private keys to PEM format
    public_key_pem = public_key.save_pkcs1().decode('utf-8')
    private_key_pem = private_key.save_pkcs1().decode('utf-8')

    # Optionally, you could associate the keys with the job_id here, for example, by saving them to a database

    return public_key_pem, private_key_pem
