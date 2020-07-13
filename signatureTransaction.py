import hashlib
import ecdsa
from collections import OrderedDict


def generate_transaction_signature(private_key, trans):
    # SECP256k1 is the Bitcoin elliptic curve
    sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    sig = sk.sign(str(trans).encode('utf'))
    vk.verify(sig, str(trans).encode('utf'))  # True



def generate_transaction_hash(tr):
    tr = OrderedDict(tr)
    return hashlib.sha256(str(tr).encode('utf8')).hexdigest()


tr = {"amount": "19", "recipient": "wghwhhqj1j1jh2h", "sender": "1ETooy6TSdJf9uED1ijhBDWJFgPac31bja",
      "timestamp": 1594603799.4893067}
# keypv = get_account_privatekey(tr['sender'])
#
# h = generate_transaction_signature(keypv,tr)
# print(h)
print(generate_transaction_hash( tr))