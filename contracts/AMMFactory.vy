# @version 0.4.3
"""
@title AMM Factory
@author Stock Trading System
@notice Factory contract for creating AMM pools
@dev Admin deploys this once, companies use it to create their own pools
"""

# Events
event PoolCreated:
    pool: indexed(address)
    stock_token: indexed(address)
    base_token: indexed(address)
    creator: address

# State variables
admin: public(address)
pool_count: public(uint256)
pools: public(HashMap[uint256, address])  # pool_id => pool_address
pool_by_tokens: public(HashMap[address, HashMap[address, address]])  # stock => base => pool

@deploy
def __init__():
    """
    @notice Initialize the AMM Factory
    """
    self.admin = msg.sender
    self.pool_count = 0

@external
def register_pool(_stock_token: address, _base_token: address, _pool_address: address):
    """
    @notice Register an AMM pool created externally
    @dev Company creates pool externally, then registers it here
    @param _stock_token Address of the stock token
    @param _base_token Address of the base token (BUSD, etc.)
    @param _pool_address Address of the created pool
    """
    assert _stock_token != empty(address), "Invalid stock token"
    assert _base_token != empty(address), "Invalid base token"
    assert _pool_address != empty(address), "Invalid pool address"
    assert _stock_token != _base_token, "Tokens must be different"
    assert self.pool_by_tokens[_stock_token][_base_token] == empty(address), "Pool already exists"

    # Store pool reference
    self.pool_count += 1
    self.pools[self.pool_count] = _pool_address
    self.pool_by_tokens[_stock_token][_base_token] = _pool_address

    log PoolCreated(_pool_address, _stock_token, _base_token, msg.sender)

@view
@external
def get_pool(_stock_token: address, _base_token: address) -> address:
    """
    @notice Get pool address for a token pair
    @param _stock_token Stock token address
    @param _base_token Base token address
    @return Pool address (empty if doesn't exist)
    """
    return self.pool_by_tokens[_stock_token][_base_token]

@view
@external
def get_pool_by_id(_pool_id: uint256) -> address:
    """
    @notice Get pool address by ID
    @param _pool_id Pool ID
    @return Pool address
    """
    assert _pool_id > 0 and _pool_id <= self.pool_count, "Invalid pool ID"
    return self.pools[_pool_id]
