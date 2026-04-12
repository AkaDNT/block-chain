#!/usr/bin/env python3
"""
Test slippage protection by simulating front-running scenarios.

This script demonstrates how slippage protection works:
1. User A calculates expected output with tight slippage (e.g., 1%)
2. User B executes a large trade first (front-running)
3. User A's transaction fails because price moved beyond slippage tolerance

Run with: `ape run test_slippage`
"""

from ape import accounts, project, networks
from ape.exceptions import ContractLogicError
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
        print("AMM pool is not initialized yet.")
        return

    print("=" * 70)
    print("SLIPPAGE PROTECTION TEST")
    print("=" * 70)

    # Load accounts
    print("\nLoading accounts...")
    try:
        user_a = accounts.load("buyer")
        user_a.set_autosign(True)
    except Exception:
        print("Account 'buyer' not found. Create with: ape accounts generate buyer")
        return

    try:
        user_b = accounts.load("frontrunner")
        user_b.set_autosign(True)
    except Exception:
        print("Account 'frontrunner' not found. Create with: ape accounts generate frontrunner")
        print("Then fund it with: ape run fund_account")
        return

    print(f"User A (buyer): {user_a.address}")
    print(f"User B (front-runner): {user_b.address}")

    # Show initial state
    print("\n" + "=" * 70)
    print("INITIAL STATE")
    print("=" * 70)
    initial_price = amm.get_price() / DECIMALS
    stock_reserve = amm.stock_reserve() / DECIMALS
    base_reserve = amm.base_reserve() / DECIMALS
    print(f"Price: {initial_price:.6f} BUSD per stock")
    print(f"Stock reserve: {stock_reserve:.2f}")
    print(f"Base reserve: {base_reserve:.2f}")

    print(f"\nUser A BUSD balance: {base_token.balanceOf(user_a.address) / DECIMALS:.2f}")
    print(f"User B stock balance: {stock_token.balanceOf(user_b.address) / DECIMALS:.2f}")

    # ============================================================
    # SCENARIO 1: Test BUY with front-running BUY
    # ============================================================
    print("\n" + "=" * 70)
    print("SCENARIO 1: BUY order front-run by another BUY")
    print("(Someone buys before you → price goes UP → you get less)")
    print("=" * 70)

    # User A wants to buy stock
    buy_amount_busd = 10000  # 10,000 BUSD
    buy_amount_wei = int(buy_amount_busd * DECIMALS)

    # Check if User A has enough balance
    if base_token.balanceOf(user_a.address) < buy_amount_wei:
        print(f"\n⚠️  User A needs {buy_amount_busd} BUSD but has {base_token.balanceOf(user_a.address) / DECIMALS:.2f}")
        print("Fund user A with BUSD first.")
    else:
        # Step 1: User A calculates expected output with 1% slippage
        expected_stock_out = amm.get_amount_out(buy_amount_wei, base_token.address)
        slippage = 1.0  # 1%
        min_stock_out = int(expected_stock_out * (1 - slippage / 100))

        print(f"\nUser A wants to buy with {buy_amount_busd} BUSD")
        print(f"Expected stock output: {expected_stock_out / DECIMALS:.6f}")
        print(f"Min acceptable (1% slippage): {min_stock_out / DECIMALS:.6f}")

        # Step 2: User B front-runs with a large buy
        frontrun_amount = int(100000 * DECIMALS)  # 100,000 BUSD buy
        if base_token.balanceOf(user_b.address) >= frontrun_amount:
            print(f"\n🏃 User B front-runs with {frontrun_amount / DECIMALS:.0f} BUSD buy...")
            base_token.approve(amm.address, frontrun_amount, sender=user_b)
            amm.swap_base_for_stock(frontrun_amount, 0, sender=user_b)  # 0 min = accept any

            new_price = amm.get_price() / DECIMALS
            price_change = ((new_price - initial_price) / initial_price) * 100
            print(f"New price after front-run: {new_price:.6f} BUSD (+{price_change:.2f}%)")

            # Step 3: User A tries to execute their buy - should FAIL
            print(f"\n📝 User A attempts buy with original min_amount_out...")
            base_token.approve(amm.address, buy_amount_wei, sender=user_a)

            try:
                amm.swap_base_for_stock(buy_amount_wei, min_stock_out, sender=user_a)
                print("❌ UNEXPECTED: Trade succeeded (slippage not triggered)")
            except ContractLogicError as e:
                if "Insufficient output amount" in str(e):
                    print("✅ SUCCESS: Transaction reverted with 'Insufficient output amount'")
                    print("   Slippage protection worked correctly!")
                else:
                    print(f"❌ Failed with different error: {e}")
            except Exception as e:
                if "Insufficient output amount" in str(e):
                    print("✅ SUCCESS: Transaction reverted with 'Insufficient output amount'")
                    print("   Slippage protection worked correctly!")
                else:
                    print(f"❌ Unexpected error: {e}")

            # Show what user A would get now
            actual_output = amm.get_amount_out(buy_amount_wei, base_token.address)
            loss_percent = ((expected_stock_out - actual_output) / expected_stock_out) * 100
            print(f"\nActual output now: {actual_output / DECIMALS:.6f} stock")
            print(f"Loss from front-run: {loss_percent:.2f}%")
        else:
            print(f"\n⚠️  User B needs BUSD to front-run. Fund the frontrunner account.")

    # ============================================================
    # SCENARIO 2: Test SELL with front-running SELL
    # ============================================================
    print("\n" + "=" * 70)
    print("SCENARIO 2: SELL order front-run by another SELL")
    print("(Someone sells before you → price goes DOWN → you get less BUSD)")
    print("=" * 70)

    # Reset price by having User B sell back (if they bought)
    user_b_stock = stock_token.balanceOf(user_b.address)
    if user_b_stock > 0:
        print(f"\nResetting: User B selling {user_b_stock / DECIMALS:.2f} stock back...")
        stock_token.approve(amm.address, user_b_stock, sender=user_b)
        amm.swap_stock_for_base(user_b_stock, 0, sender=user_b)
        print(f"Price after reset: {amm.get_price() / DECIMALS:.6f} BUSD")

    # Check if User A has stock to sell
    user_a_stock = stock_token.balanceOf(user_a.address)
    sell_amount = int(1000 * DECIMALS)  # 1000 stock tokens

    if user_a_stock >= sell_amount:
        # Reload fresh price
        fresh_price = amm.get_price() / DECIMALS

        # Step 1: User A calculates expected output with 1% slippage
        expected_busd_out = amm.get_amount_out(sell_amount, stock_token.address)
        slippage = 1.0  # 1%
        min_busd_out = int(expected_busd_out * (1 - slippage / 100))

        print(f"\nUser A wants to sell {sell_amount / DECIMALS:.0f} stock")
        print(f"Expected BUSD output: {expected_busd_out / DECIMALS:.6f}")
        print(f"Min acceptable (1% slippage): {min_busd_out / DECIMALS:.6f}")

        # Step 2: User B front-runs with a large sell
        # First give User B some stock to sell
        user_b_stock = stock_token.balanceOf(user_b.address)
        frontrun_sell = int(10000 * DECIMALS)  # 10,000 stock

        if user_b_stock >= frontrun_sell:
            print(f"\n🏃 User B front-runs with {frontrun_sell / DECIMALS:.0f} stock sell...")
            stock_token.approve(amm.address, frontrun_sell, sender=user_b)
            amm.swap_stock_for_base(frontrun_sell, 0, sender=user_b)

            new_price = amm.get_price() / DECIMALS
            price_change = ((new_price - fresh_price) / fresh_price) * 100
            print(f"New price after front-run: {new_price:.6f} BUSD ({price_change:.2f}%)")

            # Step 3: User A tries to execute their sell - should FAIL
            print(f"\n📝 User A attempts sell with original min_amount_out...")
            stock_token.approve(amm.address, sell_amount, sender=user_a)

            try:
                amm.swap_stock_for_base(sell_amount, min_busd_out, sender=user_a)
                print("❌ UNEXPECTED: Trade succeeded (slippage not triggered)")
            except ContractLogicError as e:
                if "Insufficient output amount" in str(e):
                    print("✅ SUCCESS: Transaction reverted with 'Insufficient output amount'")
                    print("   Slippage protection worked correctly!")
                else:
                    print(f"❌ Failed with different error: {e}")
            except Exception as e:
                if "Insufficient output amount" in str(e):
                    print("✅ SUCCESS: Transaction reverted with 'Insufficient output amount'")
                    print("   Slippage protection worked correctly!")
                else:
                    print(f"❌ Unexpected error: {e}")

            # Show what user A would get now
            actual_output = amm.get_amount_out(sell_amount, stock_token.address)
            loss_percent = ((expected_busd_out - actual_output) / expected_busd_out) * 100
            print(f"\nActual output now: {actual_output / DECIMALS:.6f} BUSD")
            print(f"Loss from front-run: {loss_percent:.2f}%")
        else:
            print(f"\n⚠️  User B needs stock tokens to front-run sell.")
            print(f"   User B has: {user_b_stock / DECIMALS:.2f} stock")
    else:
        print(f"\n⚠️  User A needs {sell_amount / DECIMALS:.0f} stock to test sell scenario")
        print(f"   User A has: {user_a_stock / DECIMALS:.2f} stock")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
