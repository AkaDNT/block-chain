# @version 0.4.3
"""
@title Stock Token (ERC-20)
@author Stock Trading System
@notice ERC-20 token representing company shares
"""

from ethereum.ercs import IERC20

implements: IERC20

# Events
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

# State variables
name: public(String[64])
symbol: public(String[32])
decimals: public(uint8)
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

# Company metadata
company_name: public(String[128])
ipfs_cid: public(String[64])
is_verified: public(bool)
owner: public(address)

@deploy
def __init__(
    _name: String[64],
    _symbol: String[32],
    _decimals: uint8,
    _total_supply: uint256,
    _company_name: String[128],
    _ipfs_cid: String[64]
):
    """
    @notice Initialize the stock token
    @param _name Token name
    @param _symbol Token symbol
    @param _decimals Number of decimals
    @param _total_supply Total token supply
    @param _company_name Company name
    @param _ipfs_cid IPFS CID for company documents
    """
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.totalSupply = _total_supply
    self.company_name = _company_name
    self.ipfs_cid = _ipfs_cid
    self.owner = msg.sender
    self.is_verified = False

    # Mint all tokens to the creator (company)
    self.balanceOf[msg.sender] = _total_supply
    log Transfer(empty(address), msg.sender, _total_supply)

@external
def transfer(_to: address, _value: uint256) -> bool:
    """
    @notice Transfer tokens to another address
    @param _to Recipient address
    @param _value Amount to transfer
    @return Success boolean
    """
    assert _to != empty(address), "Cannot transfer to zero address"
    assert self.balanceOf[msg.sender] >= _value, "Insufficient balance"

    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value

    log Transfer(msg.sender, _to, _value)
    return True

@external
def approve(_spender: address, _value: uint256) -> bool:
    """
    @notice Approve spender to transfer tokens on behalf of owner
    @param _spender Address to approve
    @param _value Amount to approve
    @return Success boolean
    """
    assert _spender != empty(address), "Cannot approve zero address"

    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True

@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    """
    @notice Transfer tokens from one address to another using allowance
    @param _from Source address
    @param _to Destination address
    @param _value Amount to transfer
    @return Success boolean
    """
    assert _from != empty(address), "Cannot transfer from zero address"
    assert _to != empty(address), "Cannot transfer to zero address"
    assert self.balanceOf[_from] >= _value, "Insufficient balance"
    assert self.allowance[_from][msg.sender] >= _value, "Insufficient allowance"

    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    self.allowance[_from][msg.sender] -= _value

    log Transfer(_from, _to, _value)
    return True

@external
def set_verified(_verified: bool):
    """
    @notice Set verification status (only owner)
    @param _verified Verification status
    """
    assert msg.sender == self.owner, "Only owner can set verification"
    self.is_verified = _verified

@external
def update_ipfs_cid(_new_cid: String[64]):
    """
    @notice Update IPFS CID (only owner)
    @param _new_cid New IPFS CID
    """
    assert msg.sender == self.owner, "Only owner can update CID"
    self.ipfs_cid = _new_cid
