#!/usr/bin/env python3
"""
Test IPFS file upload and retrieval

Installation:
    pip install ipfshttpclient requests

Usage:
    python scripts/test_ipfs.py <file-path>
"""

import sys
import os
import requests

def test_with_pinata(file_path, api_key=None, secret_key=None):
    """Test IPFS upload using Pinata service"""
    print("📤 Uploading to IPFS via Pinata...")

    if not api_key or not secret_key:
        print("⚠️  Pinata API keys not provided")
        print("💡 Get free API keys at: https://www.pinata.cloud/")
        return None

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": secret_key
    }

    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        result = response.json()
        cid = result['IpfsHash']
        print(f"✅ File uploaded successfully!")
        print(f"📋 CID: {cid}")
        print(f"🔗 View at:")
        print(f"   - https://ipfs.io/ipfs/{cid}")
        print(f"   - https://gateway.pinata.cloud/ipfs/{cid}")
        return cid
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def test_with_local_node(file_path):
    """Test IPFS upload using local IPFS node"""
    try:
        import ipfshttpclient

        print("📤 Uploading to local IPFS node...")

        # Connect to local IPFS daemon
        client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')

        # Add file
        result = client.add(file_path)
        cid = result['Hash']

        print(f"✅ File uploaded successfully!")
        print(f"📋 CID: {cid}")
        print(f"🔗 View at:")
        print(f"   - https://ipfs.io/ipfs/{cid}")
        print(f"   - https://gateway.pinata.cloud/ipfs/{cid}")
        print(f"   - http://localhost:8080/ipfs/{cid}")

        # Try to retrieve
        print("\n📥 Retrieving file from IPFS...")
        retrieved = client.cat(cid)

        with open(file_path, 'rb') as f:
            original = f.read()

        print(f"✅ File retrieved successfully!")
        print(f"📊 Original size: {len(original)} bytes")
        print(f"📊 Retrieved size: {len(retrieved)} bytes")
        print(f"✓ Match: {original == retrieved}")

        return cid

    except ImportError:
        print("❌ ipfshttpclient not installed")
        print("💡 Install: pip install ipfshttpclient")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("   1. Make sure IPFS daemon is running: ipfs daemon")
        print("   2. Or use Pinata service instead")
        return None

def verify_cid(cid):
    """Verify a CID is accessible via public gateways"""
    print(f"\n🔍 Verifying CID: {cid}")

    gateways = [
        f"https://ipfs.io/ipfs/{cid}",
        f"https://gateway.pinata.cloud/ipfs/{cid}",
        f"https://cloudflare-ipfs.com/ipfs/{cid}"
    ]

    for gateway in gateways:
        try:
            response = requests.head(gateway, timeout=5)
            if response.status_code == 200:
                print(f"✅ Accessible: {gateway}")
            else:
                print(f"⚠️  Not found: {gateway}")
        except Exception as e:
            print(f"❌ Failed: {gateway} - {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_ipfs.py <file-path>")
        print("Example: python test_ipfs.py ./document.pdf")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    print(f"📄 File: {file_path}")
    print(f"📊 Size: {os.path.getsize(file_path)} bytes\n")

    # Try local IPFS node first
    cid = test_with_local_node(file_path)

    # If local node fails, suggest Pinata
    if not cid:
        print("\n" + "="*50)
        print("Alternative: Use Pinata (recommended)")
        print("="*50)
        print("1. Sign up at https://www.pinata.cloud/")
        print("2. Get API keys")
        print("3. Set environment variables:")
        print("   export PINATA_API_KEY='your_api_key'")
        print("   export PINATA_SECRET_KEY='your_secret_key'")
        print("4. Run this script again")

        # Check for Pinata keys in environment
        api_key = os.getenv('PINATA_API_KEY')
        secret_key = os.getenv('PINATA_SECRET_KEY')

        if api_key and secret_key:
            print("\n🔑 Found Pinata credentials in environment")
            cid = test_with_pinata(file_path, api_key, secret_key)

    # Verify CID if we got one
    if cid:
        verify_cid(cid)

if __name__ == "__main__":
    main()
