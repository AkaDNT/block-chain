.PHONY: help install compile test node deploy frontend build clean

help:
	@echo "Community Treasury DAO"
	@echo "======================"
	@echo "make install   - Install root and frontend dependencies"
	@echo "make compile   - Compile Solidity contracts"
	@echo "make test      - Run Hardhat DAO tests"
	@echo "make node      - Start Hardhat local blockchain"
	@echo "make deploy    - Deploy DAO to localhost and export deployment.json"
	@echo "make frontend  - Start Vue DAO portal"
	@echo "make build     - Build frontend"
	@echo "make clean     - Remove generated artifacts"

install:
	npm install
	npm --prefix frontend install

compile:
	npm run compile

test:
	npm test

node:
	npm run node

deploy:
	npm run deploy:local

frontend:
	npm run frontend

build:
	npm run build

clean:
	rm -rf artifacts cache deployment.json frontend/public/deployment.json frontend/dist
