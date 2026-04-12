#!/usr/bin/env python3
"""
Setup script for initial project configuration
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None


def check_prerequisites():
    """Check if required tools are installed"""
    print("🔍 Checking prerequisites...")
    
    # Check Python
    try:
        python_version = subprocess.check_output([sys.executable, "--version"], text=True).strip()
        print(f"✅ {python_version}")
    except:
        print("❌ Python not found")
        return False
    
    # Check Node.js
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        print(f"✅ Node.js {node_version}")
    except:
        print("❌ Node.js not found")
        return False
    
    # Check Git
    try:
        git_version = subprocess.check_output(["git", "--version"], text=True).strip()
        print(f"✅ {git_version}")
    except:
        print("❌ Git not found")
        return False
    
    return True


def setup_python_environment():
    """Set up Python environment and install Ape"""
    print("\n🐍 Setting up Python environment...")
    
    # Install Ape Framework
    if run_command("pip install eth-ape", "Installing Ape Framework"):
        # Install Ape plugins
        run_command("ape plugins install vyper", "Installing Vyper plugin")
        run_command("ape plugins install geth", "Installing Geth plugin")
        return True
    return False


def setup_frontend():
    """Set up frontend dependencies"""
    print("\n🎨 Setting up frontend...")
    
    frontend_path = Path("frontend")
    if frontend_path.exists():
        os.chdir(frontend_path)
        if run_command("npm install", "Installing frontend dependencies"):
            os.chdir("..")
            return True
        os.chdir("..")
    return False


def create_env_file():
    """Create .env file from template"""
    print("\n📝 Creating environment file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_example.exists() and not env_file.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file with your actual configuration values")
        return True
    
    return False


def setup_geth_account():
    """Set up Geth development account"""
    print("\n🔐 Setting up development account...")
    
    try:
        # Check if ape accounts exist
        result = subprocess.run(["ape", "accounts", "list"], capture_output=True, text=True)
        
        if "deployer" not in result.stdout:
            print("Creating 'deployer' account...")
            print("⚠️  You'll need to run: ape accounts generate deployer")
            print("⚠️  This will prompt you to create a password for the account")
            return False
        else:
            print("✅ Deployer account already exists")
            return True
            
    except Exception as e:
        print(f"❌ Error checking accounts: {e}")
        return False


def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*60)
    print("🎉 PROJECT INITIALIZATION COMPLETE!")
    print("="*60)
    print("\n📋 NEXT STEPS:")
    print("\n1. 🔧 Configure your environment:")
    print("   - Edit .env file with your API keys and settings")
    print("   - Set up Infura project for testnet deployment")
    print("   - Configure IPFS (local node or Pinata)")
    
    print("\n2. 🔐 Create deployer account:")
    print("   ape accounts generate deployer")
    
    print("\n3. 🚀 Start local blockchain:")
    print("   geth --dev --http --http.api personal,eth,net,web3,miner --http.addr 0.0.0.0 --http.corsdomain \"*\" --allow-insecure-unlock")
    
    print("\n4. 📦 Compile and test contracts:")
    print("   ape compile")
    print("   ape test")
    
    print("\n5. 🚀 Deploy contracts:")
    print("   ape run deploy --network ethereum:local:geth-dev")
    
    print("\n6. 🎨 Start frontend:")
    print("   cd frontend")
    print("   npm run dev")
    
    print("\n📚 USEFUL COMMANDS:")
    print("   ape --help                    # Ape framework help")
    print("   ape test -v                   # Run tests with verbose output")
    print("   ape console                   # Interactive console")
    print("   ape run scripts/deploy.py     # Run deployment script")
    
    print("\n🔗 DOCUMENTATION:")
    print("   - Project README: ./README.md")
    print("   - Ape Framework: https://docs.apeworx.io/")
    print("   - Vyper: https://vyper.readthedocs.io/")
    
    print("\n" + "="*60)


def main():
    """Main setup function"""
    print("🚀 BLOCKCHAIN STOCK TRADING SYSTEM SETUP")
    print("="*50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Please install missing tools.")
        sys.exit(1)
    
    # Setup Python environment
    if not setup_python_environment():
        print("\n❌ Python environment setup failed.")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("\n❌ Frontend setup failed.")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Setup development account
    setup_geth_account()
    
    # Display next steps
    display_next_steps()


if __name__ == "__main__":
    main()
