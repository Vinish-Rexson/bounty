// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleContract {
    string public message;
    address public owner;
    address payable public constant ESCROW_WALLET = payable(0xb48Aa1f29ca8a33B9Af77125c27BEf3C78f63250);
    
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

