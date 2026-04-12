#!/usr/bin/env python3
"""
Script to initialize AMM pools for existing tokens
"""

from ape import accounts, project, Contract
import json


def main():
    """Initialize a new AMM pool"""
    
    # Load deployment info
    try:
        with open("deployment.json", "r") as f:
            deployment = json.load(f)
    except FileNotFoundError:
        print("deployment.json not found. Please run deploy.py first.")
        return
    
    # Get account
    deployer = accounts.load("deployer")
    print(f"Using account: {deployer.address}")
    
    # Load contracts
    base_token = Contract(deployment["contracts"]["BaseToken"])
    stock_token = Contract(deployment["contracts"]["StockToken_AAPL"])
    amm = Contract(deployment["contracts"]["StockAMM"])
    
    print(f"BaseToken: {base_token.address}")
    print(f"StockToken: {stock_token.address}")
    print(f"AMM: {amm.address}")
    
    # Check if pool is already initialized
    if amm.is_initialized():
        print("Pool is already initialized!")
        print(f"Stock reserve: {amm.stock_reserve() / 10**18:.2f}")
        print(f"Base reserve: {amm.base_reserve() / 10**18:.2f}")
        print(f"Current price: {amm.get_price() / 10**18:.4f} BUSD per stock")
        return
    
    # Get user input for initial liquidity
    print("\nEnter initial liquidity amounts:")
    stock_amount = float(input("Stock tokens: ")) * 10**18
    base_amount = float(input("Base tokens: ")) * 10**18
    
    print(f"\nInitializing pool with:")
    print(f"Stock tokens: {stock_amount / 10**18:.2f}")
    print(f"Base tokens: {base_amount / 10**18:.2f}")
    print(f"Initial price: {base_amount / stock_amount:.4f} BUSD per stock")
    
    # Check balances
    stock_balance = stock_token.balanceOf(deployer.address)
    base_balance = base_token.balanceOf(deployer.address)
    
    print(f"\nYour balances:")
    print(f"Stock tokens: {stock_balance / 10**18:.2f}")
    print(f"Base tokens: {base_balance / 10**18:.2f}")
    
    if stock_balance < stock_amount:
        print("Insufficient stock token balance!")
        return
    
    if base_balance < base_amount:
        print("Insufficient base token balance!")
        return
    
    # Approve tokens
    print("\nApproving tokens...")
    stock_token.approve(amm.address, int(stock_amount), sender=deployer)
    base_token.approve(amm.address, int(base_amount), sender=deployer)
    
    # Initialize pool
    print("Initializing pool...")
    tx = amm.init_pool(
        stock_token.address,
        base_token.address,
        int(stock_amount),
        int(base_amount),
        sender=deployer
    )
    
    print(f"Pool initialized! Transaction: {tx.txn_hash}")
    print(f"Final price: {amm.get_price() / 10**18:.4f} BUSD per stock")


if __name__ == "__main__":
    main()
