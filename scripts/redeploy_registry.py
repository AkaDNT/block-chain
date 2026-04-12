#!/usr/bin/env python3
"""
Redeploy Registry contract with updated permissions
"""

from ape import accounts, project
import json

def main():
    print("🔄 Redeploying Registry contract...")
    print("=" * 60)

    # Load deployer account
    deployer = accounts.load("deployer")
    print(f"👤 Deployer: {deployer.address}")

    # Deploy new Registry
    print("\n📝 Deploying Registry...")
    registry = project.Registry.deploy(sender=deployer)
    print(f"✅ Registry deployed at: {registry.address}")

    # Update deployment.json
    deployment_file = "frontend/public/deployment.json"

    try:
        with open(deployment_file, 'r') as f:
            deployment = json.load(f)
    except FileNotFoundError:
        deployment = {}

    deployment['registry'] = str(registry.address)

    with open(deployment_file, 'w') as f:
        json.dump(deployment, f, indent=2)

    print(f"\n✅ Updated {deployment_file}")

    # Update backend .env
    print("\n📝 Updating backend/.env...")
    env_file = "backend/.env"

    try:
        with open(env_file, 'r') as f:
            lines = f.readlines()

        with open(env_file, 'w') as f:
            for line in lines:
                if line.startswith('REGISTRY_ADDRESS='):
                    f.write(f'REGISTRY_ADDRESS={registry.address}\n')
                else:
                    f.write(line)

        print(f"✅ Updated {env_file}")
    except FileNotFoundError:
        print(f"⚠️  {env_file} not found, skipping")

    print("\n" + "=" * 60)
    print("✅ Registry redeployed successfully!")
    print(f"\n📋 New Registry Address: {registry.address}")
    print("\n⚠️  IMPORTANT: You need to:")
    print("   1. Re-register all companies")
    print("   2. Restart the backend server")
    print("   3. Refresh the frontend")

if __name__ == '__main__':
    main()
