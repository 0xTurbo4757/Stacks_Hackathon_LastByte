import hashlib
from inspect import signature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def hash_sha256(encoded_str):
    hashfunc = hashlib.sha256()
    hashfunc.update(encoded_str)
    return hashfunc.hexdigest()

def hash_object(obj):
    """ Return the sha256 hash of the encoded string of
        the object passed as parameter.
    """
    return hash_sha256(str(obj).encode('utf-8'))

def encoded_hash_object(obj):
    """ Return the utf-8 encoded hash of the encoded string
        of the object passed as parameter.
    """
    return hash_object(obj).encode('utf-8')


def getSHA(key, number):
    stringS = hash_object(key)   
    return (stringS[0:number])




def rsa_genkey():
    key = rsa.generate_private_key(backend=default_backend(), public_exponent=65537, \
    key_size=512)

    # get public key in OpenSSH format
    public_key = key.public_key().public_bytes(serialization.Encoding.OpenSSH, \
        serialization.PublicFormat.OpenSSH)


    # get private key in PEM container format
    pem = key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption())
    
    private_key_str = pem.decode('utf-8')
    public_key_str = public_key.decode('utf-8')

    return (public_key_str[8:], private_key_str[33:-32],key)


def generate_signature(sign, pem):
    sign = sign.encode("utf-8")
    signature = pem.sign(sign,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())

    return signature


def verify_signature(sign,string,pem):
    publickey = pem
    string = string.encode("utf-8")
    try:
        publickey.verify(sign,string,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=padding.PSS.MAX_LENGTH),hashes.SHA256())
        return True
    except Exception as e:
        print(e)
        return False
    


