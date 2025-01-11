from solcx import set_solc_version, compile_source
from web3 import Web3
import json



# Set Solidity compiler version
set_solc_version('0.8.0')

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Set default account (first account from Ganache)
w3.eth.default_account = w3.eth.accounts[0]

# First, verify the contract exists
contract_path = 'contracts/SimpleContracts.sol'
try:
    with open(contract_path, 'r') as file:
        contract_source_code = file.read()
        print(f"Successfully read contract from {contract_path}")
except FileNotFoundError:
    print(f"Error: Could not find contract at {contract_path}")
    exit(1)

# Print first few lines of contract for verification
print("\nFirst few lines of contract:")
print("\n".join(contract_source_code.split("\n")[:5]))

# Compile and deploy
compiled_sol = compile_source(contract_source_code)
contract_id = '<stdin>:SimpleContract'
if contract_id not in compiled_sol:
    print(f"Error: Contract not found in compilation output. Available contracts: {list(compiled_sol.keys())}")
    exit(1)

contract_interface = compiled_sol[contract_id]

# Print ABI for verification
print("\nGenerated ABI:")
print(json.dumps(contract_interface['abi'], indent=2))

# Deploy contract
SimpleContract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = SimpleContract.constructor("Hello, Blockchain!").transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Print contract address
print(f"Contract deployed at address: {tx_receipt.contractAddress}")

# Save contract address to a file
with open("contract_address.txt", "w") as f:
    f.write(tx_receipt.contractAddress)

# Save ABI to a file
with open("contract_abi.json", "w") as f:
    json.dump(contract_interface['abi'], f)

print("Contract address and ABI have been saved to files")