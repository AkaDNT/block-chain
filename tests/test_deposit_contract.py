import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts.test_accounts[0]


@pytest.fixture
def user():
    return accounts.test_accounts[1]


@pytest.fixture
def other_user():
    return accounts.test_accounts[2]


@pytest.fixture
def base_token(deployer):
    """Deploy BaseToken contract"""
    return deployer.deploy(project.BaseToken)


@pytest.fixture
def deposit_contract(deployer, base_token):
    """Deploy DepositContract with 2000 BUSD per ETH rate"""
    initial_rate = 2000 * 10**18  # 2000 BUSD per ETH
    contract = deployer.deploy(project.DepositContract, base_token.address, initial_rate)
    # Add deposit contract as minter for base token
    base_token.add_minter(contract.address, sender=deployer)
    return contract


class TestDepositContractDeployment:

    def test_deployment(self, deposit_contract, deployer, base_token):
        """Test DepositContract deployment"""
        assert deposit_contract.admin() == deployer.address
        assert deposit_contract.base_token() == base_token.address
        assert deposit_contract.eth_to_busd_rate() == 2000 * 10**18
        assert deposit_contract.total_eth_deposited() == 0
        assert deposit_contract.total_busd_minted() == 0

    def test_deployment_fails_with_zero_token_address(self, deployer):
        """Test deployment fails with zero token address"""
        with pytest.raises(Exception):
            deployer.deploy(
                project.DepositContract,
                "0x0000000000000000000000000000000000000000",
                2000 * 10**18
            )

    def test_deployment_fails_with_zero_rate(self, deployer, base_token):
        """Test deployment fails with zero rate"""
        with pytest.raises(Exception):
            deployer.deploy(project.DepositContract, base_token.address, 0)


class TestDeposit:

    def test_deposit_eth(self, deposit_contract, user, base_token):
        """Test depositing ETH and receiving BUSD"""
        deposit_amount = 10**18  # 1 ETH
        expected_busd = 2000 * 10**18  # 2000 BUSD

        initial_user_busd = base_token.balanceOf(user.address)

        # Deposit ETH
        tx = deposit_contract.deposit(sender=user, value=deposit_amount)

        # Check BUSD balance
        final_user_busd = base_token.balanceOf(user.address)
        assert final_user_busd == initial_user_busd + expected_busd

        # Check contract state
        assert deposit_contract.total_eth_deposited() == deposit_amount
        assert deposit_contract.total_busd_minted() == expected_busd

        # Check event
        events = tx.decode_logs(deposit_contract.Deposit)
        assert len(events) == 1
        assert events[0].user == user.address
        assert events[0].eth_amount == deposit_amount
        assert events[0].busd_amount == expected_busd

    def test_deposit_multiple_times(self, deposit_contract, user, base_token):
        """Test multiple deposits accumulate correctly"""
        deposit_amount = 10**18  # 1 ETH each time

        # First deposit
        deposit_contract.deposit(sender=user, value=deposit_amount)

        # Second deposit
        deposit_contract.deposit(sender=user, value=deposit_amount)

        # Check totals
        assert deposit_contract.total_eth_deposited() == 2 * deposit_amount
        assert deposit_contract.total_busd_minted() == 2 * 2000 * 10**18
        assert base_token.balanceOf(user.address) == 4000 * 10**18

    def test_deposit_fails_below_minimum(self, deposit_contract, user):
        """Test deposit fails below minimum amount (0.001 ETH)"""
        small_amount = 10**14  # 0.0001 ETH (below minimum)

        with pytest.raises(Exception):
            deposit_contract.deposit(sender=user, value=small_amount)

    def test_deposit_at_minimum(self, deposit_contract, user, base_token):
        """Test deposit at minimum amount succeeds"""
        min_amount = 10**15  # 0.001 ETH (minimum)

        deposit_contract.deposit(sender=user, value=min_amount)

        expected_busd = (min_amount * 2000 * 10**18) // 10**18
        assert base_token.balanceOf(user.address) == expected_busd

    def test_get_deposit_amount(self, deposit_contract):
        """Test get_deposit_amount calculation"""
        eth_amount = 5 * 10**18  # 5 ETH
        expected_busd = 10000 * 10**18  # 10000 BUSD

        result = deposit_contract.get_deposit_amount(eth_amount)
        assert result == expected_busd


class TestWithdrawal:

    def test_withdraw_busd(self, deposit_contract, deployer, user, base_token):
        """Test withdrawing BUSD and receiving ETH"""
        # First deposit ETH
        deposit_amount = 10 * 10**18  # 10 ETH
        deposit_contract.deposit(sender=user, value=deposit_amount)

        # Get initial balances
        initial_user_eth = user.balance
        initial_user_busd = base_token.balanceOf(user.address)

        # Withdraw BUSD
        withdraw_busd = 2000 * 10**18  # 2000 BUSD = 1 ETH
        base_token.approve(deposit_contract.address, withdraw_busd, sender=user)

        tx = deposit_contract.withdraw(withdraw_busd, sender=user)

        # Check balances (accounting for gas)
        final_user_busd = base_token.balanceOf(user.address)
        assert final_user_busd == initial_user_busd - withdraw_busd

        # Check contract state
        assert deposit_contract.total_eth_deposited() == deposit_amount - 10**18
        assert deposit_contract.total_busd_minted() == (10 * 2000 - 2000) * 10**18

        # Check event
        events = tx.decode_logs(deposit_contract.Withdrawal)
        assert len(events) == 1
        assert events[0].user == user.address
        assert events[0].busd_amount == withdraw_busd
        assert events[0].eth_amount == 10**18

    def test_withdraw_fails_below_minimum(self, deposit_contract, user, base_token):
        """Test withdrawal fails below minimum (1 BUSD)"""
        # First deposit
        deposit_contract.deposit(sender=user, value=10**18)

        small_amount = 10**17  # 0.1 BUSD (below minimum)
        base_token.approve(deposit_contract.address, small_amount, sender=user)

        with pytest.raises(Exception):
            deposit_contract.withdraw(small_amount, sender=user)

    def test_withdraw_fails_insufficient_busd(self, deposit_contract, user, base_token):
        """Test withdrawal fails with insufficient BUSD balance"""
        # Deposit small amount
        deposit_contract.deposit(sender=user, value=10**18)  # Get 2000 BUSD

        # Try to withdraw more than balance
        large_amount = 5000 * 10**18
        base_token.approve(deposit_contract.address, large_amount, sender=user)

        with pytest.raises(Exception):
            deposit_contract.withdraw(large_amount, sender=user)

    def test_withdraw_fails_insufficient_eth_in_contract(self, deposit_contract, deployer, user, base_token):
        """Test withdrawal fails if contract doesn't have enough ETH"""
        # Deposit ETH
        deposit_contract.deposit(sender=user, value=10**18)

        # Admin withdraws ETH from contract
        deposit_contract.emergency_withdraw_eth(10**18, sender=deployer)

        # User tries to withdraw BUSD
        withdraw_amount = 2000 * 10**18
        base_token.approve(deposit_contract.address, withdraw_amount, sender=user)

        with pytest.raises(Exception):
            deposit_contract.withdraw(withdraw_amount, sender=user)

    def test_get_withdrawal_amount(self, deposit_contract):
        """Test get_withdrawal_amount calculation"""
        busd_amount = 4000 * 10**18  # 4000 BUSD
        expected_eth = 2 * 10**18  # 2 ETH

        result = deposit_contract.get_withdrawal_amount(busd_amount)
        assert result == expected_eth


class TestAdminFunctions:

    def test_update_rate(self, deposit_contract, deployer):
        """Test admin can update rate"""
        new_rate = 3000 * 10**18  # 3000 BUSD per ETH

        deposit_contract.update_rate(new_rate, sender=deployer)

        assert deposit_contract.eth_to_busd_rate() == new_rate

    def test_update_rate_fails_non_admin(self, deposit_contract, user):
        """Test non-admin cannot update rate"""
        with pytest.raises(Exception):
            deposit_contract.update_rate(3000 * 10**18, sender=user)

    def test_update_rate_fails_zero(self, deposit_contract, deployer):
        """Test rate cannot be set to zero"""
        with pytest.raises(Exception):
            deposit_contract.update_rate(0, sender=deployer)

    def test_add_liquidity(self, deposit_contract, deployer):
        """Test admin can add liquidity"""
        initial_balance = deposit_contract.get_contract_balance()
        add_amount = 5 * 10**18

        deposit_contract.add_liquidity(sender=deployer, value=add_amount)

        assert deposit_contract.get_contract_balance() == initial_balance + add_amount

    def test_add_liquidity_fails_non_admin(self, deposit_contract, user):
        """Test non-admin cannot add liquidity"""
        with pytest.raises(Exception):
            deposit_contract.add_liquidity(sender=user, value=10**18)

    def test_add_liquidity_fails_zero_value(self, deposit_contract, deployer):
        """Test add_liquidity fails with zero value"""
        with pytest.raises(Exception):
            deposit_contract.add_liquidity(sender=deployer, value=0)

    def test_emergency_withdraw_eth(self, deposit_contract, deployer, user):
        """Test admin can emergency withdraw ETH"""
        # First add some ETH via deposit
        deposit_contract.deposit(sender=user, value=10 * 10**18)

        initial_admin_balance = deployer.balance
        withdraw_amount = 5 * 10**18

        deposit_contract.emergency_withdraw_eth(withdraw_amount, sender=deployer)

        # Admin should have received ETH (minus gas)
        assert deposit_contract.get_contract_balance() == 5 * 10**18

    def test_emergency_withdraw_fails_non_admin(self, deposit_contract, user):
        """Test non-admin cannot emergency withdraw"""
        # Add some ETH first
        deposit_contract.deposit(sender=user, value=10**18)

        with pytest.raises(Exception):
            deposit_contract.emergency_withdraw_eth(10**17, sender=user)

    def test_emergency_withdraw_fails_insufficient_balance(self, deposit_contract, deployer, user):
        """Test emergency withdraw fails with insufficient balance"""
        deposit_contract.deposit(sender=user, value=10**18)

        with pytest.raises(Exception):
            deposit_contract.emergency_withdraw_eth(10 * 10**18, sender=deployer)


class TestRateChanges:

    def test_deposit_after_rate_change(self, deposit_contract, deployer, user, base_token):
        """Test deposit uses new rate after rate change"""
        # Change rate to 3000 BUSD per ETH
        new_rate = 3000 * 10**18
        deposit_contract.update_rate(new_rate, sender=deployer)

        # Deposit 1 ETH
        deposit_contract.deposit(sender=user, value=10**18)

        # Should receive 3000 BUSD
        assert base_token.balanceOf(user.address) == 3000 * 10**18

    def test_withdrawal_after_rate_change(self, deposit_contract, deployer, user, base_token):
        """Test withdrawal uses new rate after rate change"""
        # Deposit at original rate (2000 BUSD per ETH)
        deposit_contract.deposit(sender=user, value=10 * 10**18)  # Get 20000 BUSD

        # Change rate to 4000 BUSD per ETH
        new_rate = 4000 * 10**18
        deposit_contract.update_rate(new_rate, sender=deployer)

        # Withdraw 4000 BUSD - should get 1 ETH at new rate
        withdraw_amount = 4000 * 10**18
        base_token.approve(deposit_contract.address, withdraw_amount, sender=user)

        expected_eth = deposit_contract.get_withdrawal_amount(withdraw_amount)
        assert expected_eth == 10**18  # 1 ETH


class TestContractBalance:

    def test_get_contract_balance(self, deposit_contract, user):
        """Test get_contract_balance returns correct value"""
        assert deposit_contract.get_contract_balance() == 0

        # Deposit ETH
        deposit_contract.deposit(sender=user, value=5 * 10**18)

        assert deposit_contract.get_contract_balance() == 5 * 10**18
