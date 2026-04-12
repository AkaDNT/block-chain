#!/bin/bash

echo "🚀 Starting Backend Server..."
echo "================================"

# Check if node_modules exists
if [ ! -d "backend/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd backend && npm install && cd ..
fi

# Check if contract artifacts exist
if [ ! -f "backend/contracts/StockToken.json" ]; then
    echo "📝 Exporting contract artifacts..."
    source /Users/hohoanghvy/Projects/Blockchain/blockchain-venv/bin/activate
    ape run export_contracts --network ethereum:local:node
fi

# Start the server
echo "🎯 Starting server on http://localhost:3001"
cd backend && npm start
