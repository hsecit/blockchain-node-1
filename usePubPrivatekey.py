#######################################################################################################
#       This code for encrypt the bank reuests data
#######################################################################################################
#!/usr/bin/env python

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64
import requests

BANK_URL ='http://192.168.1.5/exchange/pubkey'

def generate_keys():
    modulus_length = 1024

    key = RSA.generate(modulus_length)

    with open('private_key.pem','w') as f:
        f.write(key.export_key().decode('utf-8'))

    pub_key = key.publickey()
    # write_private_key(pub_key.export_key())
    with open('public_key.pem','w') as ff:
        ff.write(pub_key.export_key().decode('utf-8'))
  

    with open('public_key.pem','r') as ff:
        k= RSA.import_key(ff.read())
        
    print(k.export_key())
    return key, pub_key

def encrypt_private_key(a_message):
    with open('private_key.pem','r') as ff:
        private_key= RSA.import_key(ff.read())
    print(private_key)
    encryptor = PKCS1_OAEP.new(private_key)
    encrypted_msg = encryptor.encrypt(a_message)
    print(encrypted_msg)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    print(encoded_encrypted_msg)
    return encoded_encrypted_msg

def decrypt_public_key(encoded_encrypted_msg):
    with open('public_key.pem','r') as ff:
        public_key= RSA.import_key(ff.read())
    encryptor = PKCS1_OAEP.new(public_key)
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    print(decoded_encrypted_msg)
    decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
    print(decoded_decrypted_msg)
    #return decoded_decrypted_msg




def main():
  print (private)
  message = b'66699666'
  encoded = encrypt_private_key(message, public)
  decrypt_public_key(encoded, private)


def share_public_key():
    private, public = generate_keys()
    write_private_key(private)
    response = requests.post(BANK_URL,public.export_key())
    write_BANK_pub_key(response.text())
    return "success"

###################################################3
#   FOR THE SITE PRIVATE KEY
###################################################
def write_private_key(p):
     with open('my_private_key.pem','wb') as p:
        p.write(str(p).encode('utf8'))

def read_private_key():
    private =RSA.import_key(open('top.pem','rb'))
    return private


# ###################################################3
# #   FOR THE SITE BANK PUBLIC KEY
# ###################################################
# def write_BANK_pub_key(p):
#     f = open('bank_pub_key.pem','w')
#     f.write(p)
#     f.close()

# def read_BANK_pub_key():
#     f = open('bank_pub_key.pem','r')
#     p= f.read()
#     f.close()
#     return p


p = encrypt_private_key(b'hello')
print(decrypt_public_key(p))