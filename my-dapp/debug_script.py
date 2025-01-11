from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Check connection
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Sender and recipient addresses
sender_address = w3.eth.accounts[0]  # First account in Ganache
recipient_address = "0xf5F510824887603fd98Ae92900DC1C5E8B939F5c"  # Replace with actual recipient address

# Check sender's balance
sender_balance = w3.eth.get_balance(sender_address)
print(f"Sender balance: {w3.from_wei(sender_balance, 'ether')} ETH")

# Validate recipient address
if not w3.is_address(recipient_address):
    raise Exception("Invalid recipient address")
else:
    print("Recipient address is valid")
