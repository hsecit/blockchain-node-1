import pyrebase
import json
config = {
    "apiKey": "AIzaSyDi8BQjZHM0l2n1tEX5DukmyE0jQ2kctEQ",
    "authDomain": "cryptography-project-12233.firebaseapp.com",
    "databaseURL": "https://cryptography-project-12233.firebaseio.com",
    "projectId": "cryptography-project-12233",
    "storageBucket": "cryptography-project-12233.appspot.com",
    "messagingSenderId": "801611067749",
    "appId": "1:801611067749:web:19e03a535319b18cb7718c",
    "measurementId": "G-LSEMCCBFPT"
}

fire = pyrebase.initialize_app(config)


def store_blockchain(data):
    """
    this function store transactions in firebase
    :param data:
    :return:
    """
    dbase = fire.database()
    DbRef = dbase.child("Nodes")
    # the data will be the transaction(index,prev_hash,Nonce,pow,data,timestamp)
    # integrate the markle tree and private key
    DbRef.push(json.dumps(data))

