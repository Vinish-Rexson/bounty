from web3 import Web3

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))

# Check connection
if w3.is_connected():
    print("Connected to Ganache!")
else:
    print("Failed to connect.")
