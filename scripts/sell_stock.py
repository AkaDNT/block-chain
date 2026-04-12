#!/usr/bin/env python3
"""
Sell stock tokens for base tokens (BUSD) via the AMM.

Run with: `ape run sell_stock`
"""

from ape import accounts, project, networks
import json

DECIMALS = 10 ** 18


def load_deployment():
    """Load contract addresses from deployment.json."""
    try:
        with open("deployment.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("deployment.json not found. Please run deploy.py first.")
        return None


def main():
    deployment = load_deployment()
    if not deployment:
        return

    try:
        contracts = deployment["contracts"]
        base_addr = contracts["BaseToken"]
        stock_addr = contracts["StockToken_AAPL"]
        amm_addr = contracts["StockAMM"]
    except KeyError as exc:
        print(f"Missing contract address in deployment.json: {exc}")
        return

    # Choose account
    alias = input("Account alias to use (default: seller): ").strip() or "seller"
    seller = accounts.load(alias)
    seller.set_autosign(True)
    print(f"\nUsing account: {seller.address}")

    # Verify contracts exist
    provider = networks.provider
    for label, addr in [
        ("BaseToken", base_addr),
        ("StockToken_AAPL", stock_addr),
        ("StockAMM", amm_addr),
    ]:
        if provider.get_code(addr) in (b"", None):
            print(f"Contract code not found at {addr} for {label}. "
                  "Re-deploy and refresh deployment.json.")
            return

    # Load contracts
    base_token = project.BaseToken.at(base_addr)
    stock_token = project.StockToken.at(stock_addr)
    amm = project.StockAMM.at(amm_addr)

    if not amm.is_initialized():
        print("AMM pool is not initialized yet. Run init_pool.py first.")
        return

    # Current balances
    base_balance = base_token.balanceOf(seller.address)
    stock_balance = stock_token.balanceOf(seller.address)
    print(f"Current BUSD balance: {base_balance / DECIMALS:.6f}")
    print(f"Current stock balance: {stock_balance / DECIMALS:.6f}")

    if stock_balance == 0:
        print("\nNo stock tokens to sell!")
        return

    # Amount to sell
    try:
        amount_stock = float(input("\nStock tokens to sell: "))
    except ValueError:
        print("Invalid amount.")
        return

    amount_in = int(amount_stock * DECIMALS)
    if amount_in <= 0:
        print("Amount must be positive.")
        return

    if stock_balance < amount_in:
        print("Insufficient stock balance.")
        return

    # Expected output and slippage
    expected_out = amm.get_amount_out(amount_in, stock_token.address)
    if expected_out == 0:
        print("Swap would return zero BUSD. Check liquidity.")
        return

    slippage_input = input("Max slippage percent (default 1%): ").strip()
    slippage = float(slippage_input) if slippage_input else 1.0
    min_amount_out = int(expected_out * (1 - slippage / 100))

    current_price = amm.get_price() / DECIMALS
    print(f"\nExpected BUSD: {expected_out / DECIMALS:.6f}")
    print(f"Minimum after slippage: {min_amount_out / DECIMALS:.6f}")
    print(f"Current price: {current_price:.6f} BUSD per share")

    confirm = input("Proceed with swap? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Swap cancelled.")
        return

    print("\nApproving stock tokens...")
    stock_token.approve(amm.address, amount_in, sender=seller)

    print("Swapping stock for BUSD...")
    base_before = base_token.balanceOf(seller.address)
    stock_before = stock_token.balanceOf(seller.address)
    tx = amm.swap_stock_for_base(amount_in, min_amount_out, sender=seller)
    base_after = base_token.balanceOf(seller.address)
    stock_after = stock_token.balanceOf(seller.address)

    print("\n✅ Swap complete!")
    print(f"Transaction hash: {tx.txn_hash}")
    print(f"Sold stock: {(stock_before - stock_after) / DECIMALS:.6f}")
    print(f"Received BUSD: {(base_after - base_before) / DECIMALS:.6f}")
    print(f"New BUSD balance: {base_after / DECIMALS:.6f}")
    print(f"New stock balance: {stock_after / DECIMALS:.6f}")


if __name__ == "__main__":
    main()
