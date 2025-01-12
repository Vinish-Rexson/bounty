from web3 import Web3
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Connect to network
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Get private key from environment variable
ESCROW_PRIVATE_KEY = "0x2bc2a58e49df70613fdc19169cc35520b191bf38ed90a3769e7cbdcb4f04a6cd"
ESCROW_ADDRESS = "0x6182E6b60330D64bd74C0aECF13CA966d784701f"

def release_funds(contract_address, sender, recipient, amount):
    print("\n=== Release Funds Debug Info ===")
    print(f"Contract Address: {contract_address}")
    print(f"Sender Address: {sender}")
    print(f"Recipient Address: {recipient}")
    print(f"Amount: {amount}")
    print(f"Escrow Address: {ESCROW_ADDRESS}")
    
    try:
        # Check balances first
        contract_balance = w3.eth.get_balance(contract_address)
        sender_balance = w3.eth.get_balance(sender)
        recipient_balance = w3.eth.get_balance(recipient)
        escrow_balance = w3.eth.get_balance(ESCROW_ADDRESS)
        
        print("\n=== Balance Check ===")
        print(f"Contract Balance: {w3.from_wei(contract_balance, 'ether')} ETH")
        print(f"Sender Balance: {w3.from_wei(sender_balance, 'ether')} ETH")
        print(f"Recipient Balance: {w3.from_wei(recipient_balance, 'ether')} ETH")
        print(f"Escrow Balance: {w3.from_wei(escrow_balance, 'ether')} ETH")
        
        if contract_balance < w3.to_wei(amount, 'ether'):
            print(f"Error: Contract doesn't have enough funds. Needs {amount} ETH, has {w3.from_wei(contract_balance, 'ether')} ETH")
            return None
            
        # Load ABI
        with open('my_dapp/contract_abi.json', 'r') as f:
            contract_abi = json.load(f)
            print("\nABI loaded successfully")
        
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        print("Contract instance created")
        
        # Check pending transfer
        pending_amount = contract.functions.getPendingTransfer(sender, recipient).call()
        print(f"\nPending Transfer Amount: {w3.from_wei(pending_amount, 'ether')} ETH")
        
        if pending_amount == 0:
            print("Error: No pending transfer found!")
            return None
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(ESCROW_ADDRESS)
        print(f"Nonce: {nonce}")
        
        transaction = contract.functions.releaseEther(
            sender,
            recipient
        ).build_transaction({
            'from': ESCROW_ADDRESS,
            'gas': 300000,
            'nonce': nonce,
        })
        print("Transaction built")
        
        # Sign and send transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, ESCROW_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction sent. Hash: {tx_hash.hex()}")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"\nTransaction receipt: {receipt}")
        
        # Check final balances
        new_recipient_balance = w3.eth.get_balance(recipient)
        print(f"\nNew Recipient Balance: {w3.from_wei(new_recipient_balance, 'ether')} ETH")
        print(f"Balance Change: {w3.from_wei(new_recipient_balance - recipient_balance, 'ether')} ETH")
        
        return receipt
        
    except Exception as e:
        print(f"\nError in release_funds: {str(e)}")
        print("=====================================")
        raise 