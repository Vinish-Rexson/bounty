from web3 import Web3
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to network
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Get private key from environment variable
ESCROW_PRIVATE_KEY = os.getenv('ESCROW_PRIVATE_KEY')
ESCROW_ADDRESS = os.getenv('ESCROW_ADDRESS')

def release_funds(contract_address, sender, recipient, amount):
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=ABI)
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(ESCROW_ADDRESS)
    
    transaction = contract.functions.releaseEther(
        sender,
        recipient
    ).build_transaction({
        'from': ESCROW_ADDRESS,
        'gas': 300000,
        'nonce': nonce,
    })
    
    # Sign and send transaction
    signed_txn = w3.eth.account.sign_transaction(transaction, ESCROW_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    
    return w3.eth.wait_for_transaction_receipt(tx_hash) 