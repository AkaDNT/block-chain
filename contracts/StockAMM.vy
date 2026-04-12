# @version 0.4.3
"""
@title Stock AMM (Automated Market Maker)
@author Stock Trading System
@notice Constant-product AMM for trading stock tokens against base tokens
"""

from ethereum.ercs import IERC20 as ERC20

# Events
event PoolInitialized:
    stock_token: indexed(address)
    base_token: indexed(address)
    initial_stock: uint256
    initial_base: uint256

event Swap:
    trader: indexed(address)
    token_in: indexed(address)
    token_out: indexed(address)
    amount_in: uint256
    amount_out: uint256

event LiquidityAdded:
    provider: indexed(address)
    stock_amount: uint256
    base_amount: uint256

event LiquidityRemoved:
    provider: indexed(address)
    stock_amount: uint256
    base_amount: uint256

# State variables
stock_token: public(address)
base_token: public(address)
stock_reserve: public(uint256)
base_reserve: public(uint256)
fee_rate: public(uint256)  # Fee in basis points (e.g., 30 = 0.3%)
is_initialized: public(bool)

# Liquidity tracking (simplified - no LP tokens for now)
liquidity_providers: public(HashMap[address, uint256])  # Track contribution percentage
total_liquidity_shares: public(uint256)

@deploy
def __init__(_fee_rate: uint256):
    """
    @notice Initialize the AMM with fee rate
    @param _fee_rate Fee rate in basis points (30 = 0.3%)
    """
    assert _fee_rate <= 1000, "Fee rate cannot exceed 10%"
    self.fee_rate = _fee_rate
    self.is_initialized = False

@external
def init_pool(
    _stock_token: address,
    _base_token: address,
    _initial_stock: uint256,
    _initial_base: uint256
):
    """
    @notice Initialize the liquidity pool
    @param _stock_token Address of the stock token
    @param _base_token Address of the base token
    @param _initial_stock Initial stock token amount
    @param _initial_base Initial base token amount
    """
    assert not self.is_initialized, "Pool already initialized"
    assert _stock_token != empty(address), "Invalid stock token address"
    assert _base_token != empty(address), "Invalid base token address"
    assert _stock_token != _base_token, "Tokens must be different"
    assert _initial_stock > 0, "Initial stock must be positive"
    assert _initial_base > 0, "Initial base must be positive"

    self.stock_token = _stock_token
    self.base_token = _base_token

    # Transfer tokens from sender
    assert extcall ERC20(_stock_token).transferFrom(msg.sender, self, _initial_stock), "Stock transfer failed"
    assert extcall ERC20(_base_token).transferFrom(msg.sender, self, _initial_base), "Base transfer failed"

    self.stock_reserve = _initial_stock
    self.base_reserve = _initial_base
    self.is_initialized = True

    # Give initial liquidity to the provider
    initial_liquidity: uint256 = _initial_stock * _initial_base  # Geometric mean
    self.liquidity_providers[msg.sender] = initial_liquidity
    self.total_liquidity_shares = initial_liquidity

    log PoolInitialized(_stock_token, _base_token, _initial_stock, _initial_base)

@external
def swap_base_for_stock(_amount_in: uint256, _min_amount_out: uint256) -> uint256:
    """
    @notice Swap base tokens for stock tokens
    @param _amount_in Amount of base tokens to swap
    @param _min_amount_out Minimum stock tokens expected (slippage protection)
    @return Amount of stock tokens received
    """
    assert self.is_initialized, "Pool not initialized"
    assert _amount_in > 0, "Amount must be positive"

    # Calculate output amount with fee
    amount_out: uint256 = self._get_amount_out(_amount_in, self.base_reserve, self.stock_reserve)
    assert amount_out >= _min_amount_out, "Insufficient output amount"
    assert amount_out < self.stock_reserve, "Insufficient liquidity"

    # Transfer tokens
    assert extcall ERC20(self.base_token).transferFrom(msg.sender, self, _amount_in), "Base transfer failed"
    assert extcall ERC20(self.stock_token).transfer(msg.sender, amount_out), "Stock transfer failed"

    # Update reserves
    self.base_reserve += _amount_in
    self.stock_reserve -= amount_out

    log Swap(msg.sender, self.base_token, self.stock_token, _amount_in, amount_out)
    return amount_out

@external
def swap_stock_for_base(_amount_in: uint256, _min_amount_out: uint256) -> uint256:
    """
    @notice Swap stock tokens for base tokens
    @param _amount_in Amount of stock tokens to swap
    @param _min_amount_out Minimum base tokens expected (slippage protection)
    @return Amount of base tokens received
    """
    assert self.is_initialized, "Pool not initialized"
    assert _amount_in > 0, "Amount must be positive"

    # Calculate output amount with fee
    amount_out: uint256 = self._get_amount_out(_amount_in, self.stock_reserve, self.base_reserve)
    assert amount_out >= _min_amount_out, "Insufficient output amount"
    assert amount_out < self.base_reserve, "Insufficient liquidity"

    # Transfer tokens
    assert extcall ERC20(self.stock_token).transferFrom(msg.sender, self, _amount_in), "Stock transfer failed"
    assert extcall ERC20(self.base_token).transfer(msg.sender, amount_out), "Base transfer failed"

    # Update reserves
    self.stock_reserve += _amount_in
    self.base_reserve -= amount_out

    log Swap(msg.sender, self.stock_token, self.base_token, _amount_in, amount_out)
    return amount_out

@external
def add_liquidity(_stock_amount: uint256, _base_amount: uint256):
    """
    @notice Add liquidity to the pool
    @param _stock_amount Amount of stock tokens to add
    @param _base_amount Amount of base tokens to add
    """
    assert self.is_initialized, "Pool not initialized"
    assert _stock_amount > 0, "Stock amount must be positive"
    assert _base_amount > 0, "Base amount must be positive"

    # Calculate optimal amounts to maintain price ratio
    stock_needed: uint256 = _base_amount * self.stock_reserve // self.base_reserve
    base_needed: uint256 = _stock_amount * self.base_reserve // self.stock_reserve

    actual_stock: uint256 = 0
    actual_base: uint256 = 0

    if stock_needed <= _stock_amount:
        actual_stock = stock_needed
        actual_base = _base_amount
    else:
        actual_stock = _stock_amount
        actual_base = base_needed

    # Transfer tokens
    assert extcall ERC20(self.stock_token).transferFrom(msg.sender, self, actual_stock), "Stock transfer failed"
    assert extcall ERC20(self.base_token).transferFrom(msg.sender, self, actual_base), "Base transfer failed"

    # Calculate liquidity shares
    liquidity_minted: uint256 = actual_stock * actual_base
    self.liquidity_providers[msg.sender] += liquidity_minted
    self.total_liquidity_shares += liquidity_minted

    # Update reserves
    self.stock_reserve += actual_stock
    self.base_reserve += actual_base

    log LiquidityAdded(msg.sender, actual_stock, actual_base)

@view
@internal
def _get_amount_out(_amount_in: uint256, _reserve_in: uint256, _reserve_out: uint256) -> uint256:
    """
    @notice Calculate output amount for a given input (with fee)
    @param _amount_in Input amount
    @param _reserve_in Input token reserve
    @param _reserve_out Output token reserve
    @return Output amount
    """
    assert _amount_in > 0, "Amount must be positive"
    assert _reserve_in > 0 and _reserve_out > 0, "Insufficient liquidity"

    # Apply fee: amount_in_with_fee = amount_in * (10000 - fee_rate) // 10000
    amount_in_with_fee: uint256 = _amount_in * (10000 - self.fee_rate) // 10000

    # Constant product formula: x * y = k
    # amount_out = (amount_in_with_fee * reserve_out) / (reserve_in + amount_in_with_fee)
    numerator: uint256 = amount_in_with_fee * _reserve_out
    denominator: uint256 = _reserve_in + amount_in_with_fee

    return numerator // denominator

@view
@external
def get_amount_out(_amount_in: uint256, _token_in: address) -> uint256:
    """
    @notice Get expected output amount for a swap (view function)
    @param _amount_in Input amount
    @param _token_in Input token address
    @return Expected output amount
    """
    assert self.is_initialized, "Pool not initialized"

    if _token_in == self.base_token:
        return self._get_amount_out(_amount_in, self.base_reserve, self.stock_reserve)
    elif _token_in == self.stock_token:
        return self._get_amount_out(_amount_in, self.stock_reserve, self.base_reserve)
    else:
        raise "Invalid token"

@view
@external
def get_price() -> uint256:
    """
    @notice Get current price (base_reserve / stock_reserve)
    @return Current price with 18 decimals
    """
    assert self.is_initialized, "Pool not initialized"
    assert self.stock_reserve > 0, "No stock liquidity"

    # Price = base_reserve // stock_reserve (with 18 decimal precision)
    return (self.base_reserve * 10**18) // self.stock_reserve
