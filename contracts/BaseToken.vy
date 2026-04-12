# @version 0.4.3
"""
@title Base Token (ERC-20)
@author Stock Trading System
@notice Base token used for trading (represents USD or stable currency)
@dev Minters can be: DepositContract (for ETH↔BUSD), Companies (for their operations), Admin
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

event Mint:
    to: indexed(address)
    value: uint256

# State variables
name: public(String[64])
symbol: public(String[32])
decimals: public(uint8)
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])

# Admin controls
owner: public(address)
minters: public(HashMap[address, bool])

@deploy
def __init__():
    """
    @notice Initialize the base token (USD equivalent)
    """
    self.name = "Base USD Token"
    self.symbol = "BUSD"
    self.decimals = 18
    self.totalSupply = 0
    self.owner = msg.sender
    self.minters[msg.sender] = True

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
def mint(_to: address, _value: uint256):
    """
    @notice Mint new tokens (only minters)
    @param _to Address to mint to
    @param _value Amount to mint
    """
    assert self.minters[msg.sender], "Only minters can mint"
    assert _to != empty(address), "Cannot mint to zero address"

    self.totalSupply += _value
    self.balanceOf[_to] += _value

    log Transfer(empty(address), _to, _value)
    log Mint(_to, _value)

@external
def add_minter(_minter: address):
    """
    @notice Add a new minter (only owner)
    @param _minter Address to add as minter
    """
    assert msg.sender == self.owner, "Only owner can add minters"
    assert _minter != empty(address), "Cannot add zero address as minter"
    self.minters[_minter] = True

@external
def remove_minter(_minter: address):
    """
    @notice Remove a minter (only owner)
    @param _minter Address to remove as minter
    """
    assert msg.sender == self.owner, "Only owner can remove minters"
    self.minters[_minter] = False
