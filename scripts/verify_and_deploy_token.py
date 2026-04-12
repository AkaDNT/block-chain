#!/usr/bin/env python3
"""
Script to verify a company and deploy its StockToken and AMM pool
This should be run by the admin/deployer account
"""

from ape import accounts, project, networks
import json
import sys

def load_deployment():
    """Load deployment information"""
    try:
        with open('deployment.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ deployment.json not found. Please deploy contracts first.")
        sys.exit(1)

def save_deployment(data):
    """Save deployment information"""
    with open('deployment.json', 'w') as f:
        json.dump(data, f, indent=2)

def main():
    print("=" * 60)
    print("COMPANY VERIFICATION AND TOKEN DEPLOYMENT")
    print("=" * 60)

    # Load deployment info
    deployment = load_deployment()

    # Load deployer account (admin)
    deployer = accounts.load("deployer")
    deployer.set_autosign(True)

    print(f"\n👤 Admin account: {deployer.address}")
    print(f"💰 Balance: {deployer.balance / 10**18:.4f} ETH")

    # Load contracts
    registry_address = deployment['contracts']['Registry']
    base_token_address = deployment['contracts']['BaseToken']

    registry = project.Registry.at(registry_address)
    base_token = project.BaseToken.at(base_token_address)

    print(f"\n📋 Registry: {registry_address}")
    print(f"💵 Base Token (BUSD): {base_token_address}")

    # Get company count
    company_count = registry.company_count()
    print(f"\n📊 Total companies registered: {company_count}")

    if company_count == 0:
        print("❌ No companies registered yet.")
        return

    # List all companies
    print("\n" + "=" * 60)
    print("REGISTERED COMPANIES")
    print("=" * 60)

    companies = []
    for i in range(1, company_count + 1):
        company = registry.get_company(i)
        companies.append({
            'id': i,
            'name': company[2],  # name
            'symbol': company[3],  # symbol
            'owner': company[1],  # owner
            'is_verified': company[7],  # is_verified
            'stock_token': company[8],  # stock_token
            'amm_pool': company[9]  # amm_pool
        })

        status = "✅ Verified" if company[7] else "⏳ Pending"
        token_status = "✅ Deployed" if company[8] != "0x0000000000000000000000000000000000000000" else "❌ Not deployed"
        amm_status = "✅ Deployed" if company[9] != "0x0000000000000000000000000000000000000000" else "❌ Not deployed"

        print(f"\n{i}. {company[2]} ({company[3]})")
        print(f"   Owner: {company[1]}")
        print(f"   Status: {status}")
        print(f"   Token: {token_status}")
        print(f"   AMM: {amm_status}")

    # Select company to verify/deploy
    print("\n" + "=" * 60)
    company_id = int(input("Enter company ID to verify and deploy token (0 to exit): "))

    if company_id == 0:
        print("👋 Exiting...")
        return

    if company_id < 1 or company_id > company_count:
        print("❌ Invalid company ID")
        return

    selected_company = companies[company_id - 1]
    print(f"\n📌 Selected: {selected_company['name']} ({selected_company['symbol']})")

    # Step 1: Verify company
    if not selected_company['is_verified']:
        print("\n1️⃣ Verifying company...")
        confirm = input(f"   Verify {selected_company['name']}? (y/n): ")
        if confirm.lower() == 'y':
            tx = registry.set_verified(company_id, True, sender=deployer)
            print(f"   ✅ Company verified! TX: {tx.txn_hash}")
        else:
            print("   ⏭️  Skipping verification")
    else:
        print("\n1️⃣ ✅ Company already verified")

    # Step 2: Deploy StockToken
    if selected_company['stock_token'] == "0x0000000000000000000000000000000000000000":
        print("\n2️⃣ Deploying StockToken...")

        # Get token details
        print(f"\n   Company: {selected_company['name']}")
        print(f"   Symbol: {selected_company['symbol']}")

        total_supply = input("   Enter total supply (default: 1000000): ") or "1000000"
        total_supply = int(total_supply)

        # Deploy StockToken
        print(f"\n   Deploying StockToken with supply: {total_supply}...")
        stock_token = project.StockToken.deploy(
            selected_company['name'],
            selected_company['symbol'],
            total_supply,
            "QmDefault",  # Placeholder IPFS CID
            sender=deployer
        )

        print(f"   ✅ StockToken deployed at: {stock_token.address}")

        # Update registry
        print("   Updating registry with token address...")
        tx = registry.set_stock_token(company_id, stock_token.address, sender=deployer)
        print(f"   ✅ Registry updated! TX: {tx.txn_hash}")

        # Save to deployment
        deployment['contracts'][f'StockToken_{selected_company["symbol"]}'] = str(stock_token.address)
        save_deployment(deployment)

        selected_company['stock_token'] = str(stock_token.address)
    else:
        print(f"\n2️⃣ ✅ StockToken already deployed at: {selected_company['stock_token']}")
        stock_token = project.StockToken.at(selected_company['stock_token'])

    # Step 3: Deploy AMM Pool
    if selected_company['amm_pool'] == "0x0000000000000000000000000000000000000000":
        print("\n3️⃣ Deploying AMM Pool...")

        # Deploy AMM
        amm = project.StockAMM.deploy(sender=deployer)
        print(f"   ✅ AMM deployed at: {amm.address}")

        # Update registry
        print("   Updating registry with AMM address...")
        tx = registry.set_amm_pool(company_id, amm.address, sender=deployer)
        print(f"   ✅ Registry updated! TX: {tx.txn_hash}")

        # Save to deployment
        deployment['contracts'][f'StockAMM_{selected_company["symbol"]}'] = str(amm.address)
        save_deployment(deployment)

        selected_company['amm_pool'] = str(amm.address)
    else:
        print(f"\n3️⃣ ✅ AMM already deployed at: {selected_company['amm_pool']}")
        amm = project.StockAMM.at(selected_company['amm_pool'])

    # Step 4: Initialize AMM Pool
    print("\n4️⃣ Initializing AMM Pool...")

    is_initialized = amm.is_initialized()
    if is_initialized:
        print("   ✅ AMM already initialized")
    else:
        print(f"\n   Stock Token: {selected_company['stock_token']}")
        print(f"   Base Token: {base_token_address}")

        initial_stock = input("   Enter initial stock amount (default: 100000): ") or "100000"
        initial_base = input("   Enter initial base amount (default: 1000000): ") or "1000000"

        initial_stock = int(initial_stock)
        initial_base = int(initial_base)

        print(f"\n   Initial price: {initial_base / initial_stock} BUSD per {selected_company['symbol']}")

        confirm = input("   Initialize pool? (y/n): ")
        if confirm.lower() == 'y':
            # Approve tokens
            print("   Approving stock tokens...")
            tx = stock_token.approve(amm.address, initial_stock, sender=deployer)
            print(f"   ✅ Stock tokens approved")

            print("   Approving base tokens...")
            tx = base_token.approve(amm.address, initial_base, sender=deployer)
            print(f"   ✅ Base tokens approved")

            # Initialize pool
            print("   Initializing pool...")
            tx = amm.init_pool(
                stock_token.address,
                base_token.address,
                initial_stock,
                initial_base,
                sender=deployer
            )
            print(f"   ✅ Pool initialized! TX: {tx.txn_hash}")

            # Get price
            price = amm.get_price()
            print(f"   💰 Current price: {price / 10**18:.2f} BUSD per {selected_company['symbol']}")
        else:
            print("   ⏭️  Skipping initialization")

    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"\nCompany: {selected_company['name']} ({selected_company['symbol']})")
    print(f"Status: ✅ Verified")
    print(f"Stock Token: {selected_company['stock_token']}")
    print(f"AMM Pool: {selected_company['amm_pool']}")
    print("\n🎉 Company is now ready for trading!")

if __name__ == '__main__':
    main()
