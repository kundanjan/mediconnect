from web3 import Web3
from solcx import compile_standard, install_solc
import json
from eth_account import Account
from dotenv import load_dotenv
import os

Account.enable_unaudited_hdwallet_features()

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

# Account address with which you will deploy the contract
account_private_key = "0x2b905c0a4f096c2d1d0a8e1432b22439a9a273b219d4eaa4f1483c17576cafd4"

# Read the contract source code
with open("DataStorage.sol", 'r') as file:
    contract_source_code = file.read()

# Install specific Solidity version
install_solc('0.8.0')

# Compile the contract
compiled_sol = compile_standard({
    "language": "Solidity",
    "sources": {
        "DataStorage.sol": {
            "content": contract_source_code
        }
    },
    "settings": {
        "outputSelection": {
            "*": {
                "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
            }
        }
    }
}, solc_version="0.8.0")

# Get contract interface
contract_interface = compiled_sol['contracts']['DataStorage.sol']['DataStorage']

# Save ABI
with open("abi.json", 'w') as file:
    json.dump(contract_interface['abi'], file)

# Create a contract object
MyContract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['evm']['bytecode']['object'])

# Get the account address
account_address = "0x3A32e21B25b7d5bbF9FD5Cc0d54B5a1c305d4768"

# Build transaction
deploy_txn = MyContract.constructor().build_transaction({
    'from': account_address,
    'nonce': w3.eth.get_transaction_count(account_address),
    'gas': 2000000,
    'gasPrice': w3.to_wei('50', 'gwei')
})

# Sign transaction
signed_txn = w3.eth.account.sign_transaction(deploy_txn, private_key=account_private_key)

# Send transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# Wait for the transaction to be mined
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

# Print contract address
contract_address = tx_receipt['contractAddress']
print("Contract deployed at address:", contract_address)

with open("contract_address.txt", "w") as file:
    file.write(f"Contract deployed at address: {contract_address}")