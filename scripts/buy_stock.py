#!/usr/bin/env python3
"""
Buy stock tokens from the AMM using base tokens (BUSD).

Run with: `ape run buy_stock`
"""

from ape import accounts, Contract, project, networks
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
    alias = input("Account alias to use (default: buyer): ").strip() or "buyer"
    buyer = accounts.load(alias)
    buyer.set_autosign(True)
    print(f"\nUsing account: {buyer.address}")

    # Connect to contracts
    # Verify code exists at addresses to avoid ContractNotFoundError when the
    # local chain has been reset or deployment.json is stale.
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

    # Use local contract types to bind to deployed addresses
    base_token = project.BaseToken.at(base_addr)
    stock_token = project.StockToken.at(stock_addr)
    amm = project.StockAMM.at(amm_addr)

    if not amm.is_initialized():
        print("AMM pool is not initialized yet. Run init_pool.py first.")
        return

    # Current balances
    base_balance = base_token.balanceOf(buyer.address)
    stock_balance = stock_token.balanceOf(buyer.address)
    print(f"Current BUSD balance: {base_balance / DECIMALS:.6f}")
    print(f"Current stock balance: {stock_balance / DECIMALS:.6f}")

    # Amount to spend
    try:
        amount_base = float(input("\nBUSD to spend: "))
    except ValueError:
        print("Invalid amount.")
        return

    amount_in = int(amount_base * DECIMALS)
    if amount_in <= 0:
        print("Amount must be positive.")
        return

    if base_balance < amount_in:
        print("Insufficient BUSD balance.")
        return

    # Expected output and slippage
    expected_out = amm.get_amount_out(amount_in, base_token.address)
    if expected_out == 0:
        print("Swap would return zero stock tokens. Check liquidity.")
        return

    slippage_input = input("Max slippage percent (default 1%): ").strip()
    slippage = float(slippage_input) if slippage_input else 1.0
    min_amount_out = int(expected_out * (1 - slippage / 100))

    current_price = amm.get_price() / DECIMALS
    print(f"\nExpected stock tokens: {expected_out / DECIMALS:.6f}")
    print(f"Minimum after slippage: {min_amount_out / DECIMALS:.6f}")
    print(f"Current price: {current_price:.6f} BUSD per share")

    confirm = input("Proceed with swap? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Swap cancelled.")
        return

    print("\nApproving BUSD...")
    base_token.approve(amm.address, amount_in, sender=buyer)

    print("Swapping BUSD for stock...")
    base_before = base_token.balanceOf(buyer.address)
    stock_before = stock_token.balanceOf(buyer.address)
    tx = amm.swap_base_for_stock(amount_in, min_amount_out, sender=buyer)
    base_after = base_token.balanceOf(buyer.address)
    stock_after = stock_token.balanceOf(buyer.address)

    print("\n✅ Swap complete!")
    print(f"Transaction hash: {tx.txn_hash}")
    print(f"Spent BUSD: {(base_before - base_after) / DECIMALS:.6f}")
    print(f"Received stock: {(stock_after - stock_before) / DECIMALS:.6f}")
    print(f"New BUSD balance: {base_after / DECIMALS:.6f}")
    print(f"New stock balance: {stock_after / DECIMALS:.6f}")


if __name__ == "__main__":
    main()
