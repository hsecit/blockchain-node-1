import pyrebase
import requests
import json


# init firebase
conf = {
    "apiKey": "AIzaSyDi8BQjZHM0l2n1tEX5DukmyE0jQ2kctEQ",
    "authDomain": "cryptography-project-12233.firebaseapp.com",
    "databaseURL": "https://cryptography-project-12233.firebaseio.com",
    "projectId": "cryptography-project-12233",
    "storageBucket": "cryptography-project-12233.appspot.com",
    "messagingSenderId": "801611067749",
    "appId": "1:801611067749:web:19e03a535319b18cb7718c",
    "measurementId": "G-LSEMCCBFPT"
}

fire = pyrebase.initialize_app(conf)


def get_account_privatekey(addr):
    db = fire.database()
    ref = db.child("accounts").get()
    keys_uid = []
    obj_id = []
    for uid in ref.each():
        keys_uid.append(uid.key())
    for ui in keys_uid:
        ref2 = db.child("accounts").child(ui).get()
        for h in ref2.each():
            obj_id.append(h.key())

    for ui in keys_uid:
        for h in obj_id:
            r = db.child("accounts").child(ui).child(h).child("wallet").child("pair_pub_addr").child("pubaddr1").get()
            if r.val() == addr:
                return db.child("accounts").child(ui).child(h).child("wallet").child("private_key").child(
                    "hex").get().val()

