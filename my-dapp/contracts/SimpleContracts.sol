// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleContract {
    string public message;
    address public owner;
    address payable public constant ESCROW_WALLET = payable(0x686B10Bc6c6c1ad0FB47BfEF3FB50a63DD8c2994);
    mapping(address => mapping(address => uint256)) public pendingTransfers;
    
    event EtherDeposited(address sender, address recipient, uint256 amount);
    event EtherReleased(address sender, address recipient, uint256 amount);

    constructor(string memory _message) {
        message = _message;
        owner = ESCROW_WALLET;
    }

    function setMessage(string memory _newMessage) public {
        message = _newMessage;
    }

    function depositEther(address recipient) public payable {
        require(msg.value > 0, "You must send some Ether");
        (bool sent,) = ESCROW_WALLET.call{value: msg.value}("");
        require(sent, "Failed to send Ether to escrow wallet");
        
        pendingTransfers[msg.sender][recipient] += msg.value;
        emit EtherDeposited(msg.sender, recipient, msg.value);
    }

    function releaseEther(address sender, address payable recipient) public {
        require(msg.sender == ESCROW_WALLET, "Only escrow wallet can release funds");
        uint256 amount = pendingTransfers[sender][recipient];
        require(amount > 0, "No pending transfer found");
        
        // Clear the pending transfer before making the external call
        pendingTransfers[sender][recipient] = 0;
        
        // Transfer the funds
        (bool success, ) = recipient.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit EtherReleased(sender, recipient, amount);
    }

    function getPendingTransfer(address sender, address recipient) public view returns (uint256) {
        return pendingTransfers[sender][recipient];
    }
}
