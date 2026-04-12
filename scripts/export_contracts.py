#!/usr/bin/env python3
"""
Export contract ABIs and bytecode for backend deployment
"""

from ape import project
import json
import os

def export_contract(contract_name, output_dir):
    """Export contract ABI and bytecode"""
    contract = getattr(project, contract_name)

    # Get contract type
    contract_type = contract.contract_type

    # Create output
    output = {
        "abi": contract_type.abi.model_dump() if hasattr(contract_type.abi, 'model_dump') else contract_type.abi,
        "bytecode": contract_type.deployment_bytecode.bytecode if contract_type.deployment_bytecode else None
    }

    # Save to file
    output_path = os.path.join(output_dir, f"{contract_name}.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"✅ Exported {contract_name} to {output_path}")

def main():
    # Create output directory
    output_dir = "backend/contracts"
    os.makedirs(output_dir, exist_ok=True)

    print("Exporting contract ABIs and bytecode...")
    print("=" * 60)

    # Export contracts
    export_contract("StockToken", output_dir)
    export_contract("StockAMM", output_dir)
    export_contract("Registry", output_dir)
    export_contract("BaseToken", output_dir)

    print("=" * 60)
    print("✅ All contracts exported successfully!")

if __name__ == '__main__':
    main()
