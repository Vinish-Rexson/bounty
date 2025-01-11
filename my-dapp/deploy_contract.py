from solcx import set_solc_version, compile_source
from web3 import Web3
import json



# Set Solidity compiler version
set_solc_version('0.8.0')

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Set default account
w3.eth.default_account = w3.eth.accounts[0]

# Read and compile contract
contract_path = 'contracts/SimpleContracts.sol'
with open(contract_path, 'r') as file:
    contract_source_code = file.read()

# Compile contract
compiled_sol = compile_source(contract_source_code)
contract_id = '<stdin>:SimpleContract'
contract_interface = compiled_sol[contract_id]

# Deploy contract
SimpleContract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = SimpleContract.constructor("Hello, Blockchain!").transact({
    'gas': 3000000,
})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Save contract address
with open("contract_address.txt", "w") as f:
    f.write(tx_receipt.contractAddress)

# Save ABI
with open("contract_abi.json", "w") as f:
    json.dump(contract_interface['abi'], f)

print(f"Contract deployed at: {tx_receipt.contractAddress}")