import json
import time
from datetime import datetime
import requests
from flask import Flask, request,render_template,jsonify
from usePubPrivatekey import share_public_key
from blockchain_server import Block, Blockchain
from firebase_local import store_blockchain
from signatureTransaction import generate_transaction_hash
from merklelib import MerkleTree
from send_to_bank_data import send_it_now

app = Flask(__name__)


@app.route("/")
def home():
    return "hell world"


# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = set()
########################################################################################################
#           ADD TRANSACTION TO LIST OF UNCOFIRMED TRANSACTION                                          #
########################################################################################################


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    
    tx_data = request.get_json()
    
    tx_data["timestamp"] = time.time()

    print(tx_data)
    blockchain.add_new_transaction(tx_data)

    return "Success", 201
########################################################################################################
# THE MINER                                                                                            #
########################################################################################################

# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    node_chain ={
        'length': len(chain_data),
        'chain': chain_data,
        'peers': list(peers)}

    store_blockchain(node_chain)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})


@app.route('/chain_index', methods=['GET'])
def get_chain_index():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    node_chain ={
        'length': len(chain_data),
        'chain': chain_data,
        'peers': list(peers)}

    store_blockchain(node_chain)
    dataa = json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)})
    retres = json.loads(dataa)
    trans = []
    i=0
    for tr in blockchain.last_block.transactions:
        print(tr)
        i=i+1
        trans_hash = generate_transaction_hash(tr)

        trans.append({"index": i,"thash": trans_hash})
    date  = datetime.fromtimestamp(int(blockchain.last_block.timestamp))
    merklroot = MerkleTree(trans)
    data_tr ={"transactions":trans,"merkle":merklroot,"date":date}
    return render_template("blockchain.html",blockchain=retres,inf=data_tr)

# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if not result:
        return "No transactions to mine"
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


########################################################################################################
# BANK TWO FACTOR AUTH                                                                                 #
########################################################################################################
# produit + button by
# popup formulaire (num,visa,date,exp,code) valid

# /// send request 
# genrate code(randmo(8) sha256)
@app.route("/bank/buy")
def buy_online():
    share_public_key()
    return render_template("buy.html")

@app.route("/send_to_bank",methods=['POST'])
def send_data_to_bank_():
    cc_number = request.form['cc-number']
    cc_exp = request.form['cc-exp']
    ccv_code = request.form['x_card_code']
    x_zip = request.form['x_zip']
    data = {
        "cc_number":cc_number,
        "cc_exp":cc_exp,
        "ccv_code":ccv_code
    }
    print(data)
    account_status = send_it_now(data)
    print(account_status)
    return json.dumps(account_status)
########################################################################################################
#       ADD NEW NODE TO THE NETWORK                                                                    #
########################################################################################################

# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    peers.add(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()

########################################################################################################
# THW NODE RESPONSABLE TO REGISTER WITH                                                                #
########################################################################################################
@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)
    # store_transaction_blockchain(block)
    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/wait_mine')
def get_pending_tx():
    data_ =json.dumps(blockchain.unconfirmed_transactions)
    data_ready=json.loads(data_)
    return render_template("notmined.html",unchain=data_ready)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain

    longest_chain = None
    current_len = len(blockchain.chain)
    headers = {'Content-Type': "application/json"}
    for node in peers:
        try:
            response = requests.get('{}chain'.format(node), headers=headers, timeout=5)
        except requests.exceptions.ConnectionError as e:
            response = "No response"
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)


if __name__ == '__main__':
    app.run(debug=True,port=8001,host='0.0.0.0')
