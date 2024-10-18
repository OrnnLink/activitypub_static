from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate the RSA key pair
def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Get the private key in PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Get the public key in PEM format
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )
    return (private_pem, public_pem)

def write_key_to_files(private_pem, public_pem, path=""):
    with open(path +'public_key.pem', 'wb') as public_file:
        public_file.write(public_pem)

    with open(path + 'private_key.pem', 'wb') as private_file:
        private_file.write(private_pem)

"""
if __name__ == "__main__":
    private_pem, public_pem = generate_key()
    # Save the keys to files
    write_key_to_files(private_pem, public_pem)

    # Print the keys
    print('Public Key:', public_pem.decode('utf-8'))
    print('Private Key:', private_pem.decode('utf-8'))
"""