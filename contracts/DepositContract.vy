# @version 0.4.3
"""
@title Deposit Contract
@author Stock Trading System
@notice Gateway for converting ETH ↔ BUSD with 1:1 ratio for testing
@dev In production, this would integrate with a price oracle or stablecoin bridge
"""

from ethereum.ercs import IERC20 as ERC20

interface BaseToken:
    def mint(_to: address, _value: uint256): nonpayable
    def transferFrom(_from: address, _to: address, _value: uint256) -> bool: nonpayable
    def balanceOf(_owner: address) -> uint256: view

# Events
event Deposit:
    user: indexed(address)
    eth_amount: uint256
    busd_amount: uint256

event Withdrawal:
    user: indexed(address)
    busd_amount: uint256
    eth_amount: uint256

# State variables
base_token: public(address)
admin: public(address)
eth_to_busd_rate: public(uint256)  # Rate with 18 decimals (e.g., 2000 * 10^18 = 2000 BUSD per ETH)
total_eth_deposited: public(uint256)
total_busd_minted: public(uint256)

# Minimum amounts
MIN_DEPOSIT: constant(uint256) = 10**15  # 0.001 ETH minimum
MIN_WITHDRAWAL: constant(uint256) = 10**18  # 1 BUSD minimum

@deploy
def __init__(_base_token: address, _initial_rate: uint256):
    """
    @notice Initialize the deposit contract
    @param _base_token Address of the BUSD token contract
    @param _initial_rate Initial ETH to BUSD rate (with 18 decimals)
    """
    assert _base_token != empty(address), "Invalid base token address"
    assert _initial_rate > 0, "Rate must be positive"

    self.base_token = _base_token
    self.admin = msg.sender
    self.eth_to_busd_rate = _initial_rate
    self.total_eth_deposited = 0
    self.total_busd_minted = 0

@external
@payable
def deposit() -> uint256:
    """
    @notice Deposit ETH and receive BUSD
    @return Amount of BUSD received
    """
    assert msg.value >= MIN_DEPOSIT, "Deposit amount too small"

    # Calculate BUSD amount: (ETH amount * rate) / 10^18
    busd_amount: uint256 = (msg.value * self.eth_to_busd_rate) // 10**18
    assert busd_amount > 0, "BUSD amount too small"

    # Update totals
    self.total_eth_deposited += msg.value
    self.total_busd_minted += busd_amount

    # Mint BUSD to user
    extcall BaseToken(self.base_token).mint(msg.sender, busd_amount)

    log Deposit(msg.sender, msg.value, busd_amount)
    return busd_amount

@external
def withdraw(_busd_amount: uint256) -> uint256:
    """
    @notice Withdraw BUSD and receive ETH
    @param _busd_amount Amount of BUSD to withdraw
    @return Amount of ETH received
    """
    assert _busd_amount >= MIN_WITHDRAWAL, "Withdrawal amount too small"

    # Calculate ETH amount: (BUSD amount * 10^18) / rate
    eth_amount: uint256 = (_busd_amount * 10**18) // self.eth_to_busd_rate
    assert eth_amount > 0, "ETH amount too small"
    assert eth_amount <= self.balance, "Insufficient ETH in contract"

    # Check user has enough BUSD
    user_balance: uint256 = staticcall BaseToken(self.base_token).balanceOf(msg.sender)
    assert user_balance >= _busd_amount, "Insufficient BUSD balance"

    # Transfer BUSD from user to contract (will be burned or held)
    success: bool = extcall BaseToken(self.base_token).transferFrom(msg.sender, self, _busd_amount)
    assert success, "BUSD transfer failed"

    # Update totals
    self.total_eth_deposited -= eth_amount
    self.total_busd_minted -= _busd_amount

    # Send ETH to user
    send(msg.sender, eth_amount)

    log Withdrawal(msg.sender, _busd_amount, eth_amount)
    return eth_amount

@external
def update_rate(_new_rate: uint256):
    """
    @notice Update ETH to BUSD conversion rate (only admin)
    @param _new_rate New rate with 18 decimals
    @dev In production, this would be automated via oracle
    """
    assert msg.sender == self.admin, "Only admin can update rate"
    assert _new_rate > 0, "Rate must be positive"
    self.eth_to_busd_rate = _new_rate

@external
@payable
def add_liquidity():
    """
    @notice Add ETH liquidity to the contract (only admin)
    @dev Allows admin to ensure contract has enough ETH for withdrawals
    """
    assert msg.sender == self.admin, "Only admin can add liquidity"
    assert msg.value > 0, "Must send ETH"

@external
def emergency_withdraw_eth(_amount: uint256):
    """
    @notice Emergency withdrawal of ETH (only admin)
    @param _amount Amount of ETH to withdraw
    @dev Use with caution - ensure users can still withdraw their BUSD
    """
    assert msg.sender == self.admin, "Only admin can emergency withdraw"
    assert _amount <= self.balance, "Insufficient balance"
    send(self.admin, _amount)

@view
@external
def get_deposit_amount(_eth_amount: uint256) -> uint256:
    """
    @notice Calculate BUSD amount for a given ETH deposit
    @param _eth_amount Amount of ETH
    @return Expected BUSD amount
    """
    return (_eth_amount * self.eth_to_busd_rate) // 10**18

@view
@external
def get_withdrawal_amount(_busd_amount: uint256) -> uint256:
    """
    @notice Calculate ETH amount for a given BUSD withdrawal
    @param _busd_amount Amount of BUSD
    @return Expected ETH amount
    """
    return (_busd_amount * 10**18) // self.eth_to_busd_rate

@view
@external
def get_contract_balance() -> uint256:
    """
    @notice Get contract's ETH balance
    @return ETH balance
    """
    return self.balance
