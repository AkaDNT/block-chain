#!/usr/bin/env python3
"""
IPFS upload utility script
"""

import requests
import json
import os
from pathlib import Path


class IPFSUploader:
    def __init__(self, api_url="http://127.0.0.1:5001"):
        """
        Initialize IPFS uploader
        
        Args:
            api_url: IPFS API URL (default: local IPFS node)
        """
        self.api_url = api_url.rstrip('/')
        
    def upload_file(self, file_path):
        """
        Upload a file to IPFS
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            str: IPFS CID (Content Identifier)
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.api_url}/api/v0/add", files=files)
                response.raise_for_status()
                
                result = response.json()
                return result['Hash']
                
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def upload_json(self, data):
        """
        Upload JSON data to IPFS
        
        Args:
            data: Dictionary to upload as JSON
            
        Returns:
            str: IPFS CID
        """
        try:
            json_str = json.dumps(data, indent=2)
            files = {'file': ('data.json', json_str, 'application/json')}
            response = requests.post(f"{self.api_url}/api/v0/add", files=files)
            response.raise_for_status()
            
            result = response.json()
            return result['Hash']
            
        except Exception as e:
            print(f"Error uploading JSON: {e}")
            return None
    
    def get_file(self, cid, output_path=None):
        """
        Retrieve a file from IPFS
        
        Args:
            cid: IPFS Content Identifier
            output_path: Optional path to save the file
            
        Returns:
            bytes: File content
        """
        try:
            response = requests.get(f"{self.api_url}/api/v0/cat?arg={cid}")
            response.raise_for_status()
            
            if output_path:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print(f"File saved to: {output_path}")
            
            return response.content
            
        except Exception as e:
            print(f"Error retrieving file: {e}")
            return None


def create_sample_company_data():
    """Create sample company metadata"""
    return {
        "company": {
            "name": "Apple Inc",
            "symbol": "AAPL",
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "founded": "1976-04-01",
            "headquarters": "Cupertino, California, USA",
            "website": "https://www.apple.com",
            "industry": "Technology",
            "sector": "Consumer Electronics"
        },
        "financials": {
            "market_cap": "3000000000000",  # $3T
            "revenue_2023": "383285000000",  # $383.3B
            "employees": 164000,
            "currency": "USD"
        },
        "documents": {
            "prospectus": "QmProspectusCID123",
            "financial_statements": "QmFinancialsCID456",
            "legal_documents": "QmLegalCID789"
        },
        "verification": {
            "status": "pending",
            "submitted_at": "2024-01-01T00:00:00Z",
            "documents_hash": "0x1234567890abcdef"
        }
    }


def main():
    """Main function for IPFS operations"""
    uploader = IPFSUploader()
    
    print("IPFS Upload Utility")
    print("==================")
    print("1. Upload file")
    print("2. Upload sample company data")
    print("3. Retrieve file by CID")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        file_path = input("Enter file path: ").strip()
        if not os.path.exists(file_path):
            print("File not found!")
            return
        
        print(f"Uploading {file_path}...")
        cid = uploader.upload_file(file_path)
        if cid:
            print(f"File uploaded successfully!")
            print(f"IPFS CID: {cid}")
            print(f"Gateway URL: https://ipfs.io/ipfs/{cid}")
        
    elif choice == "2":
        print("Creating sample company data...")
        sample_data = create_sample_company_data()
        
        cid = uploader.upload_json(sample_data)
        if cid:
            print(f"Sample data uploaded successfully!")
            print(f"IPFS CID: {cid}")
            print(f"Gateway URL: https://ipfs.io/ipfs/{cid}")
            
            # Save CID for later use
            with open("sample_company_cid.txt", "w") as f:
                f.write(cid)
            print("CID saved to sample_company_cid.txt")
        
    elif choice == "3":
        cid = input("Enter IPFS CID: ").strip()
        output_path = input("Enter output path (optional): ").strip()
        
        print(f"Retrieving {cid}...")
        content = uploader.get_file(cid, output_path if output_path else None)
        
        if content and not output_path:
            try:
                # Try to decode as JSON
                data = json.loads(content.decode('utf-8'))
                print("Retrieved JSON data:")
                print(json.dumps(data, indent=2))
            except:
                # Print as text
                try:
                    print("Retrieved content:")
                    print(content.decode('utf-8'))
                except:
                    print(f"Retrieved binary content ({len(content)} bytes)")
    
    else:
        print("Invalid option!")


if __name__ == "__main__":
    main()
