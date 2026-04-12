#!/usr/bin/env python3
"""
Deployment script for Stock Trading System contracts
Deploys all contracts including the new TraderRegistry and DepositContract
"""

from ape import accounts, project, networks
from datetime import datetime


def main():
    """Deploy all contracts to the current network"""

    print("="*70)
    print("STOCK TRADING SYSTEM - FULL DEPLOYMENT")
    print("="*70)

    # Get deployer account
    deployer = accounts.load("deployer")  # You'll need to create this account
    deployer.set_autosign(True)  # Auto-sign all transactions
    print(f"\nDeploying with account: {deployer.address}")
    print(f"Account balance: {deployer.balance / 10**18:.4f} ETH")

    # Deploy BaseToken first
    print("\n" + "="*70)
    print("STEP 1: Deploying BaseToken (BUSD)")
    print("="*70)
    base_token = deployer.deploy(project.BaseToken)
    print(f"✅ BaseToken deployed at: {base_token.address}")

    # Mint some base tokens for testing
    print("\nMinting 1,000,000 BUSD for deployer...")
    base_token.mint(deployer.address, 1_000_000 * 10**18, sender=deployer)
    print(f"✅ Minted 1,000,000 BUSD to {deployer.address}")

    # Deploy Registry
    print("\n" + "="*70)
    print("STEP 2: Deploying Company Registry")
    print("="*70)
    registry = deployer.deploy(project.Registry)
    print(f"✅ Registry deployed at: {registry.address}")

    # Deploy MinterRegistry (for companies)
    print("\n" + "="*70)
    print("STEP 3: Deploying MinterRegistry (Company Verification)")
    print("="*70)
    minter_registry = deployer.deploy(
        project.MinterRegistry,
        base_token.address  # Pass BaseToken address as constructor argument
    )
    print(f"✅ MinterRegistry deployed at: {minter_registry.address}")

    # Deploy TraderRegistry (NEW - for individual traders)
    print("\n" + "="*70)
    print("STEP 4: Deploying TraderRegistry (Trader Verification)")
    print("="*70)
    trader_registry = deployer.deploy(project.TraderRegistry)
    print(f"✅ TraderRegistry deployed at: {trader_registry.address}")

    # Deploy DepositContract (NEW - ETH ↔ BUSD gateway)
    print("\n" + "="*70)
    print("STEP 5: Deploying DepositContract (ETH ↔ BUSD Gateway)")
    print("="*70)
    initial_rate = 2000 * 10**18  # 1 ETH = 2000 BUSD
    deposit_contract = deployer.deploy(
        project.DepositContract,
        base_token.address,
        initial_rate
    )
    print(f"✅ DepositContract deployed at: {deposit_contract.address}")
    print(f"   Initial rate: 1 ETH = {initial_rate / 10**18:.0f} BUSD")

    # Grant DepositContract minting rights
    print("\n" + "="*70)
    print("STEP 6: Configuring Permissions")
    print("="*70)
    print("Granting DepositContract minting rights on BaseToken...")
    base_token.add_minter(deposit_contract.address, sender=deployer)
    print(f"✅ DepositContract can now mint BUSD")

    # Add deployer as initial minter in BaseToken
    print("\nAdding deployer as minter in BaseToken...")
    base_token.add_minter(deployer.address, sender=deployer)
    print(f"✅ Deployer {deployer.address} is now a minter")

    # Add initial liquidity to DepositContract
    print("\nAdding initial ETH liquidity to DepositContract...")
    initial_eth_liquidity = 10 * 10**18  # 10 ETH
    deposit_contract.add_liquidity(sender=deployer, value=initial_eth_liquidity)
    print(f"✅ Added {initial_eth_liquidity / 10**18:.2f} ETH liquidity to DepositContract")

    # Add deployer as initial minter in BaseToken
    print("Adding deployer as minter in BaseToken...")
    base_token.add_minter(deployer.address, sender=deployer)
    print(f"Deployer {deployer.address} is now a minter")

    # Deploy a sample StockToken
    print("\n" + "="*70)
    print("STEP 7: Deploying Sample StockToken (AAPL)")
    print("="*70)
    stock_token = deployer.deploy(
        project.StockToken,
        "Apple Inc Stock",  # name
        "AAPL",            # symbol
        18,                # decimals
        10_000_000 * 10**18,  # total supply (10M tokens)
        "Apple Inc",       # company name
        "QmSampleCID123"   # sample IPFS CID
    )
    print(f"✅ StockToken (AAPL) deployed at: {stock_token.address}")

    # Deploy StockAMM
    print("\n" + "="*70)
    print("STEP 8: Deploying StockAMM")
    print("="*70)
    amm = deployer.deploy(
        project.StockAMM,
        30  # 0.3% fee
    )
    print(f"✅ StockAMM deployed at: {amm.address}")
    print(f"   Fee rate: 0.3%")

    # Initialize AMM pool with some liquidity
    print("\n" + "="*70)
    print("STEP 9: Initializing AMM Pool with Liquidity")
    print("="*70)

    # Approve tokens for AMM
    initial_stock = 100_000 * 10**18  # 100k stock tokens
    initial_base = 1_000_000 * 10**18  # 1M base tokens (price = 10 BUSD per stock)

    print(f"Approving {initial_stock / 10**18:.0f} AAPL for AMM...")
    stock_token.approve(amm.address, initial_stock, sender=deployer)
    print(f"Approving {initial_base / 10**18:.0f} BUSD for AMM...")
    base_token.approve(amm.address, initial_base, sender=deployer)

    # Initialize the pool
    print(f"Initializing pool...")
    amm.init_pool(
        stock_token.address,
        base_token.address,
        initial_stock,
        initial_base,
        sender=deployer
    )

    print(f"✅ Pool initialized with {initial_stock / 10**18:.0f} AAPL and {initial_base / 10**18:.0f} BUSD")
    print(f"   Initial price: {amm.get_price() / 10**18:.2f} BUSD per AAPL")

    # Deploy EncryptedDocRegistry
    print("\n" + "="*70)
    print("STEP 10: Deploying EncryptedDocRegistry")
    print("="*70)
    encrypted_doc_registry = deployer.deploy(project.EncryptedDocRegistry)
    print(f"✅ EncryptedDocRegistry deployed at: {encrypted_doc_registry.address}")

    # Register company in registry
    print("\n" + "="*70)
    print("STEP 11: Registering Sample Company in Registry")
    print("="*70)
    company_id = registry.register_company(
        "Apple Inc",
        "AAPL",
        "QmSampleProspectusCID123",  # ipfs_prospectus
        "QmSampleFinancialsCID456",  # ipfs_financials
        "QmSampleLogoCID789",        # ipfs_logo
        sender=deployer
    )

    # Set token and pool addresses in registry
    registry.set_stock_token(company_id.return_value, stock_token.address, sender=deployer)
    registry.set_amm_pool(company_id.return_value, amm.address, sender=deployer)

    print(f"✅ Company registered with ID: {company_id.return_value}")
    print(f"   Stock token linked to company")
    print(f"   AMM pool linked to company")

    # Summary
    print("\n" + "="*70)
    print("DEPLOYMENT COMPLETE! 🎉")
    print("="*70)
    print(f"\n📊 DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"Network:           {networks.active_provider.network.name}")
    print(f"Chain ID:          {networks.active_provider.chain_id}")
    print(f"Deployer:          {deployer.address}")
    print(f"Deployer Balance:  {deployer.balance / 10**18:.4f} ETH")
    print("\n📝 CORE CONTRACTS")
    print("-"*70)
    print(f"BaseToken (BUSD):        {base_token.address}")
    print(f"Registry:                {registry.address}")
    print(f"MinterRegistry:          {minter_registry.address}")
    print(f"TraderRegistry:          {trader_registry.address}  ← NEW")
    print(f"DepositContract:         {deposit_contract.address}  ← NEW")
    print(f"EncryptedDocRegistry:    {encrypted_doc_registry.address}  ← NEW")
    print("\n📝 SAMPLE DEPLOYMENT")
    print("-"*70)
    print(f"StockToken (AAPL):       {stock_token.address}")
    print(f"StockAMM:                {amm.address}")
    print(f"Company ID:              {company_id.return_value}")
    print("\n💰 LIQUIDITY INFO")
    print("-"*70)
    print(f"AMM Pool AAPL:           {initial_stock / 10**18:.0f} tokens")
    print(f"AMM Pool BUSD:           {initial_base / 10**18:.0f} tokens")
    print(f"Initial AAPL Price:      {amm.get_price() / 10**18:.2f} BUSD")
    print(f"DepositContract ETH:     {initial_eth_liquidity / 10**18:.2f} ETH")
    print(f"ETH to BUSD Rate:        1 ETH = {initial_rate / 10**18:.0f} BUSD")
    print("="*70)

    # Save deployment info
    import json
    import os

    deployment_info = {
        "network": networks.active_provider.network.name,
        "chainId": networks.active_provider.chain_id,
        "deployedAt": datetime.utcnow().isoformat() + "Z",
        "deployer": str(deployer.address),
        "contracts": {
            "BaseToken": str(base_token.address),
            "Registry": str(registry.address),
            "MinterRegistry": str(minter_registry.address),
            "TraderRegistry": str(trader_registry.address),
            "DepositContract": str(deposit_contract.address),
            "EncryptedDocRegistry": str(encrypted_doc_registry.address),
            "StockToken_AAPL": str(stock_token.address),
            "StockAMM": str(amm.address)
        },
        "sampleDeployment": {
            "companyId": int(company_id.return_value),
            "companyName": "Apple Inc",
            "companySymbol": "AAPL",
            "initialPrice": float(amm.get_price() / 10**18)
        },
        "config": {
            "ethToBusdRate": int(initial_rate),
            "ammFeeRate": 30,  # 0.3% in basis points
            "depositContractInitialLiquidity": float(initial_eth_liquidity / 10**18)
        }
    }

    print("\n💾 Saving deployment information...")

    # Save to project root
    with open("deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    print("✅ Deployment info saved to deployment.json")

    # Also save to frontend/public for web app access
    frontend_path = os.path.join("frontend", "public", "deployment.json")
    os.makedirs(os.path.dirname(frontend_path), exist_ok=True)
    with open(frontend_path, "w") as f:
        json.dump(deployment_info, f, indent=2)
    print(f"✅ Deployment info also saved to {frontend_path}")

    print("\n" + "="*70)
    print("🚀 NEXT STEPS:")
    print("="*70)
    print("1. Update your .env file with contract addresses (if needed)")
    print("2. Verify contracts on block explorer (optional)")
    print("3. Test the deposit/withdraw functionality")
    print("4. Test trader KYC flow")
    print("5. Test trading with the sample AAPL token")
    print("="*70)
    print("\n✨ All systems ready! Your stock trading platform is deployed!\n")


if __name__ == "__main__":
    main()
