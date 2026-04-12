import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts.test_accounts[0]


@pytest.fixture
def trader():
    return accounts.test_accounts[1]


@pytest.fixture
def base_token(deployer):
    """Deploy BaseToken contract"""
    return deployer.deploy(project.BaseToken)


@pytest.fixture
def stock_token(deployer):
    """Deploy StockToken contract"""
    return deployer.deploy(
        project.StockToken,
        "Test Stock",
        "TEST",
        18,
        1_000_000 * 10**18,  # 1M tokens
        "Test Company",
        "QmTestCID123"
    )


@pytest.fixture
def amm(deployer):
    """Deploy StockAMM contract"""
    return deployer.deploy(project.StockAMM, 30)  # 0.3% fee


@pytest.fixture
def initialized_amm(deployer, trader, base_token, stock_token, amm):
    """AMM with initialized pool"""
    # Mint base tokens for deployer and trader
    base_token.mint(deployer.address, 10_000_000 * 10**18, sender=deployer)
    base_token.mint(trader.address, 1_000_000 * 10**18, sender=deployer)
    
    # Transfer some stock tokens to trader
    stock_token.transfer(trader.address, 100_000 * 10**18, sender=deployer)
    
    # Initialize pool with 100k stock and 1M base (price = 10)
    initial_stock = 100_000 * 10**18
    initial_base = 1_000_000 * 10**18
    
    stock_token.approve(amm.address, initial_stock, sender=deployer)
    base_token.approve(amm.address, initial_base, sender=deployer)
    
    amm.init_pool(
        stock_token.address,
        base_token.address,
        initial_stock,
        initial_base,
        sender=deployer
    )
    
    return amm


class TestStockAMM:
    
    def test_deployment(self, amm):
        """Test AMM deployment"""
        assert amm.fee_rate() == 30
        assert not amm.is_initialized()
    
    def test_pool_initialization(self, deployer, base_token, stock_token, amm):
        """Test pool initialization"""
        # Mint and approve tokens
        base_token.mint(deployer.address, 1_000_000 * 10**18, sender=deployer)
        
        initial_stock = 100_000 * 10**18
        initial_base = 1_000_000 * 10**18
        
        stock_token.approve(amm.address, initial_stock, sender=deployer)
        base_token.approve(amm.address, initial_base, sender=deployer)
        
        # Initialize pool
        tx = amm.init_pool(
            stock_token.address,
            base_token.address,
            initial_stock,
            initial_base,
            sender=deployer
        )
        
        # Check state
        assert amm.is_initialized()
        assert amm.stock_token() == stock_token.address
        assert amm.base_token() == base_token.address
        assert amm.stock_reserve() == initial_stock
        assert amm.base_reserve() == initial_base
        
        # Check price (should be 10 base per stock)
        expected_price = (initial_base * 10**18) // initial_stock
        assert amm.get_price() == expected_price
        
        # Check event
        events = tx.decode_logs(amm.PoolInitialized)
        assert len(events) == 1
        assert events[0].stock_token == stock_token.address
        assert events[0].base_token == base_token.address
    
    def test_cannot_initialize_twice(self, initialized_amm, deployer, base_token, stock_token):
        """Test that pool cannot be initialized twice"""
        stock_token.approve(initialized_amm.address, 1000 * 10**18, sender=deployer)
        base_token.approve(initialized_amm.address, 1000 * 10**18, sender=deployer)
        
        with pytest.raises(Exception):
            initialized_amm.init_pool(
                stock_token.address,
                base_token.address,
                1000 * 10**18,
                1000 * 10**18,
                sender=deployer
            )
    
    def test_swap_base_for_stock(self, initialized_amm, trader, base_token, stock_token):
        """Test swapping base tokens for stock tokens"""
        # Get initial balances
        initial_base_balance = base_token.balanceOf(trader.address)
        initial_stock_balance = stock_token.balanceOf(trader.address)
        
        # Swap 10,000 base for stock
        swap_amount = 10_000 * 10**18
        base_token.approve(initialized_amm.address, swap_amount, sender=trader)
        
        # Get expected output
        expected_output = initialized_amm.get_amount_out(swap_amount, base_token.address)
        
        # Perform swap
        tx = initialized_amm.swap_base_for_stock(swap_amount, 0, sender=trader)
        
        # Check balances
        final_base_balance = base_token.balanceOf(trader.address)
        final_stock_balance = stock_token.balanceOf(trader.address)
        
        assert final_base_balance == initial_base_balance - swap_amount
        assert final_stock_balance == initial_stock_balance + expected_output
        
        # Check event
        events = tx.decode_logs(initialized_amm.Swap)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].amount_in == swap_amount
        assert events[0].amount_out == expected_output
    
    def test_swap_stock_for_base(self, initialized_amm, trader, base_token, stock_token):
        """Test swapping stock tokens for base tokens"""
        # Get initial balances
        initial_base_balance = base_token.balanceOf(trader.address)
        initial_stock_balance = stock_token.balanceOf(trader.address)
        
        # Swap 1,000 stock for base
        swap_amount = 1_000 * 10**18
        stock_token.approve(initialized_amm.address, swap_amount, sender=trader)
        
        # Get expected output
        expected_output = initialized_amm.get_amount_out(swap_amount, stock_token.address)
        
        # Perform swap
        tx = initialized_amm.swap_stock_for_base(swap_amount, 0, sender=trader)
        
        # Check balances
        final_base_balance = base_token.balanceOf(trader.address)
        final_stock_balance = stock_token.balanceOf(trader.address)
        
        assert final_stock_balance == initial_stock_balance - swap_amount
        assert final_base_balance == initial_base_balance + expected_output
        
        # Check event
        events = tx.decode_logs(initialized_amm.Swap)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].amount_in == swap_amount
        assert events[0].amount_out == expected_output
    
    def test_slippage_protection(self, initialized_amm, trader, base_token):
        """Test slippage protection works"""
        swap_amount = 10_000 * 10**18
        base_token.approve(initialized_amm.address, swap_amount, sender=trader)
        
        # Get expected output
        expected_output = initialized_amm.get_amount_out(swap_amount, base_token.address)
        
        # Try to swap with higher minimum output (should fail)
        with pytest.raises(Exception):
            initialized_amm.swap_base_for_stock(
                swap_amount, 
                expected_output + 1000 * 10**18,  # Higher than expected
                sender=trader
            )
    
    def test_price_impact(self, initialized_amm, trader, base_token):
        """Test that large swaps have price impact"""
        # Get initial price
        initial_price = initialized_amm.get_price()
        
        # Perform large swap (100k base tokens)
        large_swap = 100_000 * 10**18
        base_token.approve(initialized_amm.address, large_swap, sender=trader)
        initialized_amm.swap_base_for_stock(large_swap, 0, sender=trader)
        
        # Check that price increased (more base per stock)
        final_price = initialized_amm.get_price()
        assert final_price > initial_price
    
    def test_add_liquidity(self, initialized_amm, trader, base_token, stock_token):
        """Test adding liquidity to the pool"""
        # Get initial reserves
        initial_stock_reserve = initialized_amm.stock_reserve()
        initial_base_reserve = initialized_amm.base_reserve()
        
        # Add liquidity
        stock_amount = 10_000 * 10**18
        base_amount = 100_000 * 10**18  # Maintain 1:10 ratio
        
        stock_token.approve(initialized_amm.address, stock_amount, sender=trader)
        base_token.approve(initialized_amm.address, base_amount, sender=trader)
        
        tx = initialized_amm.add_liquidity(stock_amount, base_amount, sender=trader)
        
        # Check reserves increased
        final_stock_reserve = initialized_amm.stock_reserve()
        final_base_reserve = initialized_amm.base_reserve()
        
        assert final_stock_reserve > initial_stock_reserve
        assert final_base_reserve > initial_base_reserve
        
        # Check event
        events = tx.decode_logs(initialized_amm.LiquidityAdded)
        assert len(events) == 1
        assert events[0].stock_amount > 0
        assert events[0].base_amount > 0
    
    def test_fee_calculation(self, initialized_amm, trader, base_token):
        """Test that fees are properly calculated"""
        swap_amount = 10_000 * 10**18
        
        # Calculate expected output with and without fees
        # Without fee: output = (input * reserve_out) / (reserve_in + input)
        stock_reserve = initialized_amm.stock_reserve()
        base_reserve = initialized_amm.base_reserve()
        
        # With 0.3% fee, effective input is 99.7% of actual input
        effective_input = swap_amount * 9970 // 10000
        expected_output = (effective_input * stock_reserve) // (base_reserve + effective_input)
        
        # Get actual output from contract
        actual_output = initialized_amm.get_amount_out(swap_amount, base_token.address)
        
        # Should be very close (within rounding errors)
        assert abs(actual_output - expected_output) <= 1
    
    def test_zero_liquidity_fails(self, amm, deployer, base_token, stock_token):
        """Test that operations fail with zero liquidity"""
        # Try to swap without initializing pool
        with pytest.raises(Exception):
            amm.swap_base_for_stock(1000 * 10**18, 0, sender=deployer)
    
    def test_insufficient_balance_fails(self, initialized_amm, trader, base_token):
        """Test that swaps fail with insufficient balance"""
        # Try to swap more than balance
        trader_balance = base_token.balanceOf(trader.address)
        excessive_amount = trader_balance + 1000 * 10**18
        
        base_token.approve(initialized_amm.address, excessive_amount, sender=trader)
        
        with pytest.raises(Exception):
            initialized_amm.swap_base_for_stock(excessive_amount, 0, sender=trader)
