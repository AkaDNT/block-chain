#!/usr/bin/env python3
"""
Fund an account with ETH from the deployer account
"""

from ape import accounts, networks
from eth_utils import to_checksum_address

def main():
    """Send ETH to a specified account"""

    # Get deployer account (has ETH)
    deployer = accounts.load("deployer")
    deployer.set_autosign(True)

    print(f"Deployer address: {deployer.address}")
    print(f"Deployer balance: {deployer.balance / 10**18:.4f} ETH")

    # Get recipient address
    recipient = input("\nEnter recipient address: ").strip()

    # Convert to checksum address
    try:
        recipient = to_checksum_address(recipient)
    except Exception as e:
        print(f"Error: Invalid address format - {e}")
        return

    # Get amount to send
    amount_eth = float(input("Enter amount of ETH to send: "))
    amount_wei = int(amount_eth * 10**18)

    # Confirm
    print(f"\nSending {amount_eth} ETH to {recipient}")
    confirm = input("Confirm? (yes/no): ").strip().lower()

    if confirm == 'yes':
        # Send ETH
        tx = deployer.transfer(recipient, amount_wei)
        print(f"\n✅ Transaction successful!")
        print(f"Transaction hash: {tx.txn_hash}")
        print(f"New balance of {recipient}: {networks.provider.get_balance(recipient) / 10**18:.4f} ETH")
        print(f"Remaining deployer balance: {deployer.balance / 10**18:.4f} ETH")
    else:
        print("Transaction cancelled")

if __name__ == "__main__":
    main()
