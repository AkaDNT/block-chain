import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts[0]


@pytest.fixture
def user1():
    return accounts[1]


@pytest.fixture
def user2():
    return accounts[2]


@pytest.fixture
def base_token(deployer):
    """Deploy BaseToken contract"""
    return deployer.deploy(project.BaseToken)


@pytest.fixture
def stock_token(deployer):
    """Deploy StockToken contract"""
    return deployer.deploy(
        project.StockToken,
        "Apple Inc Stock",
        "AAPL",
        18,
        1_000_000 * 10**18,  # 1M tokens
        "Apple Inc",
        "QmAppleCID123"
    )


class TestBaseToken:
    
    def test_deployment(self, base_token, deployer):
        """Test BaseToken deployment"""
        assert base_token.name() == "Base USD Token"
        assert base_token.symbol() == "BUSD"
        assert base_token.decimals() == 18
        assert base_token.totalSupply() == 0
        assert base_token.owner() == deployer.address
        assert base_token.minters(deployer.address) == True
    
    def test_mint(self, base_token, deployer, user1):
        """Test minting tokens"""
        mint_amount = 1000 * 10**18
        
        # Mint tokens
        tx = base_token.mint(user1.address, mint_amount, sender=deployer)
        
        # Check balances and supply
        assert base_token.balanceOf(user1.address) == mint_amount
        assert base_token.totalSupply() == mint_amount
        
        # Check events
        events = tx.decode_logs(base_token.Transfer)
        assert len(events) == 1
        assert events[0].sender == "0x0000000000000000000000000000000000000000"
        assert events[0].receiver == user1.address
        assert events[0].value == mint_amount
        
        mint_events = tx.decode_logs(base_token.Mint)
        assert len(mint_events) == 1
        assert mint_events[0].to == user1.address
        assert mint_events[0].value == mint_amount
    
    def test_only_minters_can_mint(self, base_token, user1):
        """Test that only minters can mint"""
        with pytest.raises(Exception):
            base_token.mint(user1.address, 1000 * 10**18, sender=user1)
    
    def test_add_remove_minter(self, base_token, deployer, user1):
        """Test adding and removing minters"""
        # Add minter
        base_token.add_minter(user1.address, sender=deployer)
        assert base_token.minters(user1.address) == True
        
        # User1 can now mint
        base_token.mint(user1.address, 1000 * 10**18, sender=user1)
        assert base_token.balanceOf(user1.address) == 1000 * 10**18
        
        # Remove minter
        base_token.remove_minter(user1.address, sender=deployer)
        assert base_token.minters(user1.address) == False
        
        # User1 can no longer mint
        with pytest.raises(Exception):
            base_token.mint(user1.address, 1000 * 10**18, sender=user1)
    
    def test_only_owner_can_manage_minters(self, base_token, user1, user2):
        """Test that only owner can add/remove minters"""
        with pytest.raises(Exception):
            base_token.add_minter(user2.address, sender=user1)
        
        with pytest.raises(Exception):
            base_token.remove_minter(user1.address, sender=user1)
    
    def test_transfer(self, base_token, deployer, user1, user2):
        """Test token transfers"""
        # Mint tokens to user1
        mint_amount = 1000 * 10**18
        base_token.mint(user1.address, mint_amount, sender=deployer)
        
        # Transfer tokens
        transfer_amount = 300 * 10**18
        tx = base_token.transfer(user2.address, transfer_amount, sender=user1)
        
        # Check balances
        assert base_token.balanceOf(user1.address) == mint_amount - transfer_amount
        assert base_token.balanceOf(user2.address) == transfer_amount
        
        # Check event
        events = tx.decode_logs(base_token.Transfer)
        assert len(events) == 1
        assert events[0].sender == user1.address
        assert events[0].receiver == user2.address
        assert events[0].value == transfer_amount
    
    def test_approve_and_transfer_from(self, base_token, deployer, user1, user2):
        """Test approve and transferFrom"""
        # Mint tokens to user1
        mint_amount = 1000 * 10**18
        base_token.mint(user1.address, mint_amount, sender=deployer)
        
        # Approve user2 to spend tokens
        approve_amount = 500 * 10**18
        tx = base_token.approve(user2.address, approve_amount, sender=user1)
        
        # Check allowance
        assert base_token.allowance(user1.address, user2.address) == approve_amount
        
        # Check approval event
        events = tx.decode_logs(base_token.Approval)
        assert len(events) == 1
        assert events[0].owner == user1.address
        assert events[0].spender == user2.address
        assert events[0].value == approve_amount
        
        # Transfer from user1 to deployer via user2
        transfer_amount = 200 * 10**18
        tx = base_token.transferFrom(user1.address, deployer.address, transfer_amount, sender=user2)
        
        # Check balances and allowance
        assert base_token.balanceOf(user1.address) == mint_amount - transfer_amount
        assert base_token.balanceOf(deployer.address) == transfer_amount
        assert base_token.allowance(user1.address, user2.address) == approve_amount - transfer_amount


class TestStockToken:
    
    def test_deployment(self, stock_token, deployer):
        """Test StockToken deployment"""
        assert stock_token.name() == "Apple Inc Stock"
        assert stock_token.symbol() == "AAPL"
        assert stock_token.decimals() == 18
        assert stock_token.totalSupply() == 1_000_000 * 10**18
        assert stock_token.company_name() == "Apple Inc"
        assert stock_token.ipfs_cid() == "QmAppleCID123"
        assert stock_token.owner() == deployer.address
        assert stock_token.is_verified() == False
        
        # All tokens should be minted to deployer
        assert stock_token.balanceOf(deployer.address) == 1_000_000 * 10**18
    
    def test_transfer(self, stock_token, deployer, user1):
        """Test stock token transfers"""
        transfer_amount = 10_000 * 10**18
        
        tx = stock_token.transfer(user1.address, transfer_amount, sender=deployer)
        
        assert stock_token.balanceOf(deployer.address) == 1_000_000 * 10**18 - transfer_amount
        assert stock_token.balanceOf(user1.address) == transfer_amount
        
        # Check event
        events = tx.decode_logs(stock_token.Transfer)
        assert len(events) == 1
        assert events[0].sender == deployer.address
        assert events[0].receiver == user1.address
        assert events[0].value == transfer_amount
    
    def test_approve_and_transfer_from(self, stock_token, deployer, user1, user2):
        """Test approve and transferFrom for stock tokens"""
        # Approve user1 to spend tokens
        approve_amount = 50_000 * 10**18
        stock_token.approve(user1.address, approve_amount, sender=deployer)
        
        # Transfer from deployer to user2 via user1
        transfer_amount = 20_000 * 10**18
        stock_token.transferFrom(deployer.address, user2.address, transfer_amount, sender=user1)
        
        # Check balances and allowance
        assert stock_token.balanceOf(deployer.address) == 1_000_000 * 10**18 - transfer_amount
        assert stock_token.balanceOf(user2.address) == transfer_amount
        assert stock_token.allowance(deployer.address, user1.address) == approve_amount - transfer_amount
    
    def test_set_verified(self, stock_token, deployer, user1):
        """Test setting verification status"""
        # Only owner can set verification
        stock_token.set_verified(True, sender=deployer)
        assert stock_token.is_verified() == True
        
        # Non-owner cannot set verification
        with pytest.raises(Exception):
            stock_token.set_verified(False, sender=user1)
    
    def test_update_ipfs_cid(self, stock_token, deployer, user1):
        """Test updating IPFS CID"""
        new_cid = "QmNewAppleCID456"
        
        # Only owner can update CID
        stock_token.update_ipfs_cid(new_cid, sender=deployer)
        assert stock_token.ipfs_cid() == new_cid
        
        # Non-owner cannot update CID
        with pytest.raises(Exception):
            stock_token.update_ipfs_cid("QmHackerCID", sender=user1)
    
    def test_cannot_transfer_to_zero_address(self, stock_token, deployer):
        """Test that transfers to zero address fail"""
        with pytest.raises(Exception):
            stock_token.transfer("0x0000000000000000000000000000000000000000", 1000, sender=deployer)
    
    def test_insufficient_balance_fails(self, stock_token, user1):
        """Test that transfers fail with insufficient balance"""
        # user1 has no tokens
        with pytest.raises(Exception):
            stock_token.transfer(user1.address, 1000, sender=user1)
    
    def test_insufficient_allowance_fails(self, stock_token, deployer, user1, user2):
        """Test that transferFrom fails with insufficient allowance"""
        # Approve small amount
        stock_token.approve(user1.address, 1000, sender=deployer)
        
        # Try to transfer more than approved
        with pytest.raises(Exception):
            stock_token.transferFrom(deployer.address, user2.address, 2000, sender=user1)
