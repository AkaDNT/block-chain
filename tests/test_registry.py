import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts[0]


@pytest.fixture
def company_owner():
    return accounts[1]


@pytest.fixture
def verifier():
    return accounts[2]


@pytest.fixture
def user():
    return accounts[3]


@pytest.fixture
def registry(deployer):
    """Deploy Registry contract"""
    return deployer.deploy(project.Registry)


class TestRegistry:
    
    def test_deployment(self, registry, deployer):
        """Test Registry deployment"""
        assert registry.admin() == deployer.address
        assert registry.verifiers(deployer.address) == True
        assert registry.company_count() == 0
    
    def test_register_company(self, registry, company_owner):
        """Test company registration"""
        # Register company
        tx = registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Check company count
        assert registry.company_count() == 1
        
        # Check mappings
        assert registry.owner_to_company(company_owner.address) == 1
        assert registry.symbol_to_company("AAPL") == 1
        
        # Get company details
        company = registry.get_company(1)
        assert company.id == 1
        assert company.owner == company_owner.address
        assert company.name == "Apple Inc"
        assert company.symbol == "AAPL"
        assert company.ipfs_cid == "QmAppleCID123"
        assert company.is_verified == False
        assert company.stock_token == "0x0000000000000000000000000000000000000000"
        assert company.amm_pool == "0x0000000000000000000000000000000000000000"
        
        # Check event
        events = tx.decode_logs(registry.CompanyRegistered)
        assert len(events) == 1
        assert events[0].company_id == 1
        assert events[0].owner == company_owner.address
        assert events[0].name == "Apple Inc"
        assert events[0].symbol == "AAPL"
        assert events[0].ipfs_cid == "QmAppleCID123"
    
    def test_cannot_register_duplicate_symbol(self, registry, company_owner, user):
        """Test that duplicate symbols are not allowed"""
        # Register first company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Try to register with same symbol
        with pytest.raises(Exception):
            registry.register_company(
                "Another Apple",
                "AAPL",
                "QmAnotherCID456",
                sender=user
            )
    
    def test_cannot_register_multiple_companies_same_owner(self, registry, company_owner):
        """Test that one address can only register one company"""
        # Register first company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Try to register another company with same owner
        with pytest.raises(Exception):
            registry.register_company(
                "Microsoft Corp",
                "MSFT",
                "QmMicrosoftCID456",
                sender=company_owner
            )
    
    def test_empty_fields_fail(self, registry, company_owner):
        """Test that empty fields cause registration to fail"""
        # Empty name
        with pytest.raises(Exception):
            registry.register_company("", "AAPL", "QmCID123", sender=company_owner)
        
        # Empty symbol
        with pytest.raises(Exception):
            registry.register_company("Apple Inc", "", "QmCID123", sender=company_owner)
        
        # Empty CID
        with pytest.raises(Exception):
            registry.register_company("Apple Inc", "AAPL", "", sender=company_owner)
    
    def test_set_verified(self, registry, deployer, company_owner, user):
        """Test setting company verification"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Verify company (deployer is verifier by default)
        tx = registry.set_verified(1, True, sender=deployer)
        
        # Check verification status
        company = registry.get_company(1)
        assert company.is_verified == True
        
        # Check event
        events = tx.decode_logs(registry.CompanyVerified)
        assert len(events) == 1
        assert events[0].company_id == 1
        assert events[0].verified_by == deployer.address
        
        # Unverify company
        registry.set_verified(1, False, sender=deployer)
        company = registry.get_company(1)
        assert company.is_verified == False
        
        # Non-verifier cannot set verification
        with pytest.raises(Exception):
            registry.set_verified(1, True, sender=user)
    
    def test_add_remove_verifier(self, registry, deployer, verifier, user):
        """Test adding and removing verifiers"""
        # Add verifier
        registry.add_verifier(verifier.address, sender=deployer)
        assert registry.verifiers(verifier.address) == True
        
        # Register company to test verification
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=user
        )
        
        # New verifier can verify
        registry.set_verified(1, True, sender=verifier)
        company = registry.get_company(1)
        assert company.is_verified == True
        
        # Remove verifier
        registry.remove_verifier(verifier.address, sender=deployer)
        assert registry.verifiers(verifier.address) == False
        
        # Removed verifier cannot verify
        with pytest.raises(Exception):
            registry.set_verified(1, False, sender=verifier)
    
    def test_only_admin_can_manage_verifiers(self, registry, user, verifier):
        """Test that only admin can add/remove verifiers"""
        # Non-admin cannot add verifier
        with pytest.raises(Exception):
            registry.add_verifier(verifier.address, sender=user)
        
        # Non-admin cannot remove verifier
        with pytest.raises(Exception):
            registry.remove_verifier(verifier.address, sender=user)
    
    def test_update_ipfs_cid(self, registry, company_owner, user):
        """Test updating IPFS CID"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Update CID
        new_cid = "QmNewAppleCID456"
        tx = registry.update_ipfs_cid(1, new_cid, sender=company_owner)
        
        # Check updated CID
        company = registry.get_company(1)
        assert company.ipfs_cid == new_cid
        
        # Check event
        events = tx.decode_logs(registry.IPFSUpdated)
        assert len(events) == 1
        assert events[0].company_id == 1
        assert events[0].old_cid == "QmAppleCID123"
        assert events[0].new_cid == new_cid
        
        # Non-owner cannot update CID
        with pytest.raises(Exception):
            registry.update_ipfs_cid(1, "QmHackerCID", sender=user)
    
    def test_set_stock_token(self, registry, company_owner, user):
        """Test setting stock token address"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Set stock token address
        token_address = "0x1234567890123456789012345678901234567890"
        registry.set_stock_token(1, token_address, sender=company_owner)
        
        # Check token address
        company = registry.get_company(1)
        assert company.stock_token == token_address
        
        # Non-owner cannot set token
        with pytest.raises(Exception):
            registry.set_stock_token(1, token_address, sender=user)
    
    def test_set_amm_pool(self, registry, company_owner, user):
        """Test setting AMM pool address"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Set AMM pool address
        pool_address = "0x1234567890123456789012345678901234567890"
        registry.set_amm_pool(1, pool_address, sender=company_owner)
        
        # Check pool address
        company = registry.get_company(1)
        assert company.amm_pool == pool_address
        
        # Non-owner cannot set pool
        with pytest.raises(Exception):
            registry.set_amm_pool(1, pool_address, sender=user)
    
    def test_get_company_by_symbol(self, registry, company_owner):
        """Test getting company by symbol"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Get company by symbol
        company = registry.get_company_by_symbol("AAPL")
        assert company.id == 1
        assert company.name == "Apple Inc"
        assert company.symbol == "AAPL"
        
        # Non-existent symbol should fail
        with pytest.raises(Exception):
            registry.get_company_by_symbol("MSFT")
    
    def test_get_company_by_owner(self, registry, company_owner):
        """Test getting company by owner"""
        # Register company
        registry.register_company(
            "Apple Inc",
            "AAPL",
            "QmAppleCID123",
            sender=company_owner
        )
        
        # Get company by owner
        company = registry.get_company_by_owner(company_owner.address)
        assert company.id == 1
        assert company.name == "Apple Inc"
        assert company.owner == company_owner.address
        
        # Non-existent owner should fail
        with pytest.raises(Exception):
            registry.get_company_by_owner(accounts[9].address)
    
    def test_invalid_company_id_fails(self, registry, deployer):
        """Test that invalid company IDs cause failures"""
        # Get non-existent company
        with pytest.raises(Exception):
            registry.get_company(1)
        
        # Set verification for non-existent company
        with pytest.raises(Exception):
            registry.set_verified(1, True, sender=deployer)
