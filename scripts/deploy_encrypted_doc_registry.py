#!/usr/bin/env python3
"""
Deployment script for EncryptedDocRegistry contract
Handles encrypted IPFS document storage with ACL-based key management
"""

from ape import accounts, project, networks
from datetime import datetime
import json
import os


def main():
    """Deploy EncryptedDocRegistry contract"""

    print("="*70)
    print("ENCRYPTED DOCUMENT REGISTRY - DEPLOYMENT")
    print("="*70)

    # Get deployer account
    deployer = accounts.load("deployer")
    deployer.set_autosign(True)
    print(f"\nDeploying with account: {deployer.address}")
    print(f"Account balance: {deployer.balance / 10**18:.4f} ETH")

    # Deploy EncryptedDocRegistry
    print("\n" + "="*70)
    print("Deploying EncryptedDocRegistry")
    print("="*70)
    encrypted_doc_registry = deployer.deploy(project.EncryptedDocRegistry)
    print(f"✅ EncryptedDocRegistry deployed at: {encrypted_doc_registry.address}")

    # Summary
    print("\n" + "="*70)
    print("DEPLOYMENT COMPLETE! 🎉")
    print("="*70)
    print(f"\n📊 DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"Network:                  {networks.active_provider.network.name}")
    print(f"Chain ID:                 {networks.active_provider.chain_id}")
    print(f"Deployer:                 {deployer.address}")
    print(f"EncryptedDocRegistry:     {encrypted_doc_registry.address}")
    print("="*70)

    # Update deployment.json
    print("\n💾 Updating deployment information...")

    deployment_file = "deployment.json"
    deployment_info = {}

    if os.path.exists(deployment_file):
        with open(deployment_file, "r") as f:
            deployment_info = json.load(f)

    # Add or update EncryptedDocRegistry
    if "contracts" not in deployment_info:
        deployment_info["contracts"] = {}

    deployment_info["contracts"]["EncryptedDocRegistry"] = str(encrypted_doc_registry.address)
    deployment_info["encryptedDocRegistryDeployedAt"] = datetime.utcnow().isoformat() + "Z"

    with open(deployment_file, "w") as f:
        json.dump(deployment_info, f, indent=2)
    print(f"✅ Updated {deployment_file}")

    # Also update frontend deployment file
    frontend_path = os.path.join("frontend", "public", "deployment.json")
    if os.path.exists(frontend_path):
        with open(frontend_path, "r") as f:
            frontend_deployment = json.load(f)

        if "contracts" not in frontend_deployment:
            frontend_deployment["contracts"] = {}

        frontend_deployment["contracts"]["EncryptedDocRegistry"] = str(encrypted_doc_registry.address)

        with open(frontend_path, "w") as f:
            json.dump(frontend_deployment, f, indent=2)
        print(f"✅ Updated {frontend_path}")

    print("\n" + "="*70)
    print("🚀 USAGE:")
    print("="*70)
    print("1. Import the contract address in your frontend:")
    print(f"   const ENCRYPTED_DOC_REGISTRY = '{encrypted_doc_registry.address}'")
    print("")
    print("2. Use the Vue components:")
    print("   <EncryptedDocumentUpload :contract-address=\"address\" :signer=\"signer\" />")
    print("   <EncryptedDocumentList :contract-address=\"address\" :signer=\"signer\" />")
    print("="*70)


if __name__ == "__main__":
    main()
