from ape import accounts, project

def main():
    # Load deployer account
    deployer = accounts.test_accounts[0]

    # Get base token address from existing deployment
    # You'll need to update this with your actual BaseToken address
    base_token_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Update this!

    print(f"Deploying MinterRegistry with deployer: {deployer.address}")
    print(f"Base Token Address: {base_token_address}")

    # Deploy MinterRegistry
    minter_registry = project.MinterRegistry.deploy(
        base_token_address,
        sender=deployer
    )

    print(f"\n✅ MinterRegistry deployed at: {minter_registry.address}")
    print(f"\nAdd this to your .env file:")
    print(f"VITE_MINTER_REGISTRY_ADDRESS={minter_registry.address}")

    return minter_registry

if __name__ == "__main__":
    main()
