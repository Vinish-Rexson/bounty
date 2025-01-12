from solcx import set_solc_version, compile_source
from web3 import Web3
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get escrow address from environment
ESCROW_ADDRESS = "0x6182E6b60330D64bd74C0aECF13CA966d784701f"

# Set Solidity compiler version
set_solc_version('0.8.0')

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
if not w3.is_connected():
    raise Exception("Failed to connect to Ganache")

# Set default account
w3.eth.default_account = w3.eth.accounts[0]

# Read and compile contract with escrow address
contract_source = '''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleContract {
    string public message;
    address public owner;
    address payable public constant ESCROW_WALLET = payable(0x6182E6b60330D64bd74C0aECF13CA966d784701f);
    
    struct Transfer {
        uint256 amount;
        bool firstApproval;
        bool secondApproval;
    }
    
    mapping(address => mapping(address => Transfer)) public pendingTransfers;
    
    event EtherDeposited(address sender, address recipient, uint256 amount);
    event EtherReleased(address sender, address recipient, uint256 amount);

    constructor(string memory _message) {
        message = _message;
        owner = msg.sender;
    }

    function depositEther(address recipient) public payable {
        require(msg.value > 0, "Must send some ETH");
        pendingTransfers[msg.sender][recipient] = Transfer({
            amount: msg.value,
            firstApproval: false,
            secondApproval: false
        });
        emit EtherDeposited(msg.sender, recipient, msg.value);
    }

    function releaseEther(address sender, address payable recipient) public {
        require(msg.sender == ESCROW_WALLET, "Only escrow can release");
        require(pendingTransfers[sender][recipient].amount > 0, "No pending transfer");
        
        uint256 amount = pendingTransfers[sender][recipient].amount;
        delete pendingTransfers[sender][recipient];
        
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit EtherReleased(sender, recipient, amount);
    }

    function getPendingTransfer(address sender, address recipient) public view returns (uint256) {
        return pendingTransfers[sender][recipient].amount;
    }
}
'''

# Compile and deploy contract
compiled_sol = compile_source(contract_source)
contract_id = '<stdin>:SimpleContract'
contract_interface = compiled_sol[contract_id]

print(f"\n=== Contract Deployment Debug Info ===")
print(f"Escrow Address: {ESCROW_ADDRESS}")
print("Compiling contract...")

# Deploy contract with initial message
SimpleContract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])
tx_hash = SimpleContract.constructor("Initial contract message").transact()
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Contract Address: {tx_receipt.contractAddress}")
print("Contract deployed successfully!")
print("=====================================\n")

# Save contract address
with open("contract_address.txt", "w") as f:
    f.write(tx_receipt.contractAddress)

# Save ABI
with open("contract_abi.json", "w") as f:
    json.dump(contract_interface['abi'], f)

print("Contract address and ABI saved to files")