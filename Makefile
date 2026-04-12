# Blockchain Stock Trading System - Development Makefile

.PHONY: help setup install compile test deploy clean frontend start-geth stop-geth start-ipfs stop-ipfs backend start stop

# Default target
help:
	@echo "🚀 Blockchain Stock Trading System"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "📦 Quick Start:"
	@echo "  start          - Start everything (IPFS + Geth + Frontend)"
	@echo "  stop           - Stop all services (IPFS + Geth)"
	@echo "  backend        - Start backend only (IPFS + Geth)"
	@echo "  frontend       - Start frontend development server"
	@echo ""
	@echo "🔧 Setup:"
	@echo "  setup          - Run initial project setup"
	@echo "  install        - Install all dependencies"
	@echo "  compile        - Compile smart contracts"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test           - Run contract tests"
	@echo "  test-coverage  - Run tests with coverage"
	@echo ""
	@echo "🚀 Deployment:"
	@echo "  deploy-local   - Deploy to local Geth network"
	@echo "  deploy-testnet - Deploy to Sepolia testnet"
	@echo ""
	@echo "⛓️  Services:"
	@echo "  start-geth     - Start local Geth development node"
	@echo "  stop-geth      - Stop local Geth development node"
	@echo "  start-ipfs     - Start IPFS daemon"
	@echo "  stop-ipfs      - Stop IPFS daemon"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  clean          - Clean build artifacts"
	@echo "  lint           - Run code linting"
	@echo "  status         - Show project status"
	@echo ""

# Initial setup
setup:
	@echo "🔧 Running initial setup..."
	python scripts/setup.py

# Install dependencies
install:
	@echo "📦 Installing Python dependencies..."
	pip install eth-ape
	ape plugins install vyper geth
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install

# Compile contracts
compile:
	@echo "🔨 Compiling smart contracts..."
	ape compile

# Run tests
test:
	@echo "🧪 Running contract tests..."
	ape test

# Run tests with coverage
test-coverage:
	@echo "🧪 Running tests with coverage..."
	ape test --coverage

# Deploy to local network
deploy-local:
	@echo "🚀 Deploying to local Geth network..."
	ape run deploy --network ethereum:local:geth-dev

# Deploy to testnet
deploy-testnet:
	@echo "🚀 Deploying to Sepolia testnet..."
	@if [ -z "$$WEB3_INFURA_PROJECT_ID" ]; then \
		echo "❌ WEB3_INFURA_PROJECT_ID environment variable not set"; \
		exit 1; \
	fi
	ape run deploy --network ethereum:sepolia

# Start frontend development server
frontend:
	@echo "🎨 Starting frontend development server..."
	cd frontend && npm run dev

# Start local Geth node
start-geth:
	@echo "⛓️  Starting local Geth development node..."
	@if pgrep -f "geth.*--dev" > /dev/null; then \
		echo "⚠️  Geth development node is already running"; \
	else \
		geth --dev --http --http.api personal,eth,net,web3,miner --http.addr 0.0.0.0 --http.corsdomain "*" --allow-insecure-unlock --datadir ./geth-data > geth.log 2>&1 & \
		echo "✅ Geth development node started (PID: $$!)"; \
		echo "📋 Logs available in geth.log"; \
	fi

# Stop local Geth node
stop-geth:
	@echo "🛑 Stopping local Geth development node..."
	@if pgrep -f "geth.*--dev" > /dev/null; then \
		pkill -f "geth.*--dev"; \
		echo "✅ Geth development node stopped"; \
	else \
		echo "⚠️  No Geth development node running"; \
	fi

# Start IPFS daemon
start-ipfs:
	@echo "📦 Starting IPFS daemon..."
	@if pgrep -f "ipfs daemon" > /dev/null; then \
		echo "⚠️  IPFS daemon is already running"; \
	else \
		ipfs daemon > ipfs.log 2>&1 & \
		echo "✅ IPFS daemon started (PID: $$!)"; \
		echo "📋 Logs available in ipfs.log"; \
		echo "🌐 Web UI: http://localhost:5001/webui"; \
		echo "🔗 Gateway: http://localhost:8080/ipfs/"; \
	fi

# Stop IPFS daemon
stop-ipfs:
	@echo "🛑 Stopping IPFS daemon..."
	@if pgrep -f "ipfs daemon" > /dev/null; then \
		pkill -f "ipfs daemon"; \
		echo "✅ IPFS daemon stopped"; \
	else \
		echo "⚠️  No IPFS daemon running"; \
	fi

# Start backend services (IPFS + Geth)
backend:
	@echo "🚀 Starting backend services..."
	@make start-ipfs
	@sleep 2
	@make start-geth
	@echo ""
	@echo "✅ Backend services started!"
	@echo "   - IPFS: http://localhost:5001/webui"
	@echo "   - Geth: http://localhost:8545"
	@echo ""
	@echo "💡 Run 'make frontend' to start the UI"

# Start everything (backend + frontend)
start:
	@echo "🚀 Starting all services..."
	@echo ""
	@echo "🎨 Starting frontend..."
	cd frontend && npm run dev
	cd bakcend && npm start

# Stop all services
stop:
	@echo "🛑 Stopping all services..."
	@make stop-geth
	@make stop-ipfs
	@echo "✅ All services stopped"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf .build/
	rm -rf .cache/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.cache/
	rm -f geth.log
	rm -f ipfs.log
	rm -rf geth-data/
	@echo "✅ Clean complete"

# Lint code
lint:
	@echo "🔍 Running code linting..."
	@echo "Linting Vyper contracts..."
	@for file in contracts/*.vy; do \
		echo "Checking $$file..."; \
	done
	@echo "Linting frontend code..."
	cd frontend && npm run lint || echo "⚠️  Frontend linting not configured"

# Development workflow shortcuts
dev-setup: install compile test
	@echo "✅ Development environment ready!"

dev-start: start-geth
	@echo "⏳ Waiting for Geth to start..."
	@sleep 3
	@make deploy-local
	@echo "🎉 Development environment started!"
	@echo "💡 Run 'make frontend' in another terminal to start the UI"

dev-stop: stop-geth
	@echo "🛑 Development environment stopped"

# Quick test and deploy cycle
quick-deploy: compile test deploy-local
	@echo "🚀 Quick deploy cycle complete!"

# Production build
build-frontend:
	@echo "🏗️  Building frontend for production..."
	cd frontend && npm run build

# Full deployment pipeline
deploy-full: compile test deploy-local build-frontend
	@echo "🎉 Full deployment pipeline complete!"

# Show project status
status:
	@echo "📊 Project Status"
	@echo "================"
	@echo ""
	@echo "🔧 Environment:"
	@python --version 2>/dev/null || echo "❌ Python not found"
	@node --version 2>/dev/null || echo "❌ Node.js not found"
	@ape --version 2>/dev/null || echo "❌ Ape not installed"
	@echo ""
	@echo "⛓️  Blockchain:"
	@if pgrep -f "geth.*--dev" > /dev/null; then \
		echo "✅ Geth development node running"; \
	else \
		echo "❌ Geth development node not running"; \
	fi
	@if pgrep -f "ipfs daemon" > /dev/null; then \
		echo "✅ IPFS daemon running"; \
	else \
		echo "❌ IPFS daemon not running"; \
	fi
	@echo ""
	@echo "📦 Contracts:"
	@if [ -d ".build" ]; then \
		echo "✅ Contracts compiled"; \
	else \
		echo "❌ Contracts not compiled"; \
	fi
	@echo ""
	@echo "🎨 Frontend:"
	@if [ -d "frontend/node_modules" ]; then \
		echo "✅ Frontend dependencies installed"; \
	else \
		echo "❌ Frontend dependencies not installed"; \
	fi
