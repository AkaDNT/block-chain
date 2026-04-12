import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts[0]


@pytest.fixture
def trader():
    return accounts[1]


@pytest.fixture
def verifier():
    return accounts[2]


@pytest.fixture
def other_user():
    return accounts[3]


@pytest.fixture
def trader_registry(deployer):
    """Deploy TraderRegistry contract"""
    return deployer.deploy(project.TraderRegistry)


@pytest.fixture
def sample_kyc_data():
    """Sample KYC data for trader registration"""
    return {
        "full_name": "Jane Smith",
        "email": "jane.smith@email.com",
        "country": "United States",
        "ipfs_id_document": "QmIdDocumentCID123456789012345678901234567890",
        "ipfs_selfie": "QmSelfieCID12345678901234567890123456789012345"
    }


class TestTraderRegistryDeployment:

    def test_deployment(self, trader_registry, deployer):
        """Test TraderRegistry deployment"""
        assert trader_registry.admin() == deployer.address
        assert trader_registry.kyc_count() == 0
        assert trader_registry.verifiers(deployer.address) == True

    def test_admin_is_verifier_by_default(self, trader_registry, deployer):
        """Test that admin is a verifier by default"""
        assert trader_registry.verifiers(deployer.address) == True


class TestSubmitKYC:

    def test_submit_kyc(self, trader_registry, trader, sample_kyc_data):
        """Test submitting KYC for trader verification"""
        tx = trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        # Check KYC count
        assert trader_registry.kyc_count() == 1

        # Check address mapping
        assert trader_registry.address_to_kyc(trader.address) == 1

        # Check KYC details
        kyc = trader_registry.get_kyc(1)
        assert kyc.id == 1
        assert kyc.trader == trader.address
        assert kyc.full_name == sample_kyc_data["full_name"]
        assert kyc.email == sample_kyc_data["email"]
        assert kyc.country == sample_kyc_data["country"]
        assert kyc.ipfs_id_document == sample_kyc_data["ipfs_id_document"]
        assert kyc.ipfs_selfie == sample_kyc_data["ipfs_selfie"]
        assert kyc.status == 0  # PENDING
        assert kyc.verified_by == "0x0000000000000000000000000000000000000000"

        # Check event
        events = tx.decode_logs(trader_registry.TraderRegistered)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].request_id == 1
        assert events[0].full_name == sample_kyc_data["full_name"]

    def test_cannot_submit_kyc_twice(self, trader_registry, trader, sample_kyc_data):
        """Test that same address cannot submit KYC twice"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                "Different Name",
                sample_kyc_data["email"],
                sample_kyc_data["country"],
                sample_kyc_data["ipfs_id_document"],
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )

    def test_submit_fails_empty_full_name(self, trader_registry, trader, sample_kyc_data):
        """Test submit fails with empty full name"""
        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                "",
                sample_kyc_data["email"],
                sample_kyc_data["country"],
                sample_kyc_data["ipfs_id_document"],
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )

    def test_submit_fails_empty_email(self, trader_registry, trader, sample_kyc_data):
        """Test submit fails with empty email"""
        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                sample_kyc_data["full_name"],
                "",
                sample_kyc_data["country"],
                sample_kyc_data["ipfs_id_document"],
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )

    def test_submit_fails_empty_country(self, trader_registry, trader, sample_kyc_data):
        """Test submit fails with empty country"""
        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                "",
                sample_kyc_data["ipfs_id_document"],
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )

    def test_submit_fails_empty_id_document(self, trader_registry, trader, sample_kyc_data):
        """Test submit fails with empty ID document"""
        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["country"],
                "",
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )

    def test_submit_fails_empty_selfie(self, trader_registry, trader, sample_kyc_data):
        """Test submit fails with empty selfie"""
        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["country"],
                sample_kyc_data["ipfs_id_document"],
                "",
                sender=trader
            )


class TestVerifyTrader:

    def test_verify_trader(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test verifier can verify a trader"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        tx = trader_registry.verify_trader(1, sender=deployer)

        # Check KYC status
        kyc = trader_registry.get_kyc(1)
        assert kyc.status == 1  # VERIFIED
        assert kyc.verified_by == deployer.address
        assert kyc.verified_at > 0

        # Check verified trader status
        assert trader_registry.verified_traders(trader.address) == True
        assert trader_registry.is_verified_trader(trader.address) == True

        # Check event
        events = tx.decode_logs(trader_registry.TraderVerified)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].verified_by == deployer.address
        assert events[0].request_id == 1

    def test_verify_fails_non_verifier(self, trader_registry, trader, other_user, sample_kyc_data):
        """Test non-verifier cannot verify traders"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        with pytest.raises(Exception):
            trader_registry.verify_trader(1, sender=other_user)

    def test_verify_fails_invalid_kyc_id(self, trader_registry, deployer):
        """Test verify fails with invalid KYC ID"""
        with pytest.raises(Exception):
            trader_registry.verify_trader(999, sender=deployer)

    def test_verify_fails_already_verified(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test cannot verify already verified trader"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        trader_registry.verify_trader(1, sender=deployer)

        with pytest.raises(Exception):
            trader_registry.verify_trader(1, sender=deployer)

    def test_verified_trader_cannot_submit_again(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test verified trader cannot submit new KYC"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        trader_registry.verify_trader(1, sender=deployer)

        with pytest.raises(Exception):
            trader_registry.submit_kyc(
                "New Name",
                sample_kyc_data["email"],
                sample_kyc_data["country"],
                sample_kyc_data["ipfs_id_document"],
                sample_kyc_data["ipfs_selfie"],
                sender=trader
            )


class TestRejectTrader:

    def test_reject_trader(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test verifier can reject a trader"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        rejection_reason = "ID document is not clear"
        tx = trader_registry.reject_trader(1, rejection_reason, sender=deployer)

        # Check KYC status
        kyc = trader_registry.get_kyc(1)
        assert kyc.status == 2  # REJECTED
        assert kyc.verified_by == deployer.address
        assert kyc.rejection_reason == rejection_reason

        # Check not verified
        assert trader_registry.verified_traders(trader.address) == False

        # Check address mapping cleared (allows re-submission)
        assert trader_registry.address_to_kyc(trader.address) == 0

        # Check event
        events = tx.decode_logs(trader_registry.TraderRejected)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].rejected_by == deployer.address
        assert events[0].request_id == 1
        assert events[0].rejection_reason == rejection_reason

    def test_reject_fails_non_verifier(self, trader_registry, trader, other_user, sample_kyc_data):
        """Test non-verifier cannot reject traders"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        with pytest.raises(Exception):
            trader_registry.reject_trader(1, "Rejected", sender=other_user)

    def test_reject_fails_empty_reason(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test reject fails with empty rejection reason"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        with pytest.raises(Exception):
            trader_registry.reject_trader(1, "", sender=deployer)

    def test_can_resubmit_after_rejection(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test trader can resubmit KYC after rejection"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        trader_registry.reject_trader(1, "ID not clear", sender=deployer)

        # Resubmit with new documents
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            "QmNewIdDocumentCID1234567890123456789012345678",
            "QmNewSelfieCID123456789012345678901234567890123",
            sender=trader
        )

        assert trader_registry.kyc_count() == 2
        assert trader_registry.address_to_kyc(trader.address) == 2


class TestRevokeTrader:

    def test_revoke_trader(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test admin can revoke trader verification"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )
        trader_registry.verify_trader(1, sender=deployer)

        tx = trader_registry.revoke_trader(trader.address, sender=deployer)

        # Check status
        kyc = trader_registry.get_kyc(1)
        assert kyc.status == 3  # REVOKED
        assert trader_registry.verified_traders(trader.address) == False

        # Check event
        events = tx.decode_logs(trader_registry.TraderRevoked)
        assert len(events) == 1
        assert events[0].trader == trader.address
        assert events[0].revoked_by == deployer.address

    def test_revoke_fails_non_admin(self, trader_registry, deployer, trader, verifier, sample_kyc_data):
        """Test non-admin cannot revoke traders (even verifiers)"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )
        trader_registry.verify_trader(1, sender=deployer)

        # Add verifier
        trader_registry.add_verifier(verifier.address, sender=deployer)

        # Verifier cannot revoke
        with pytest.raises(Exception):
            trader_registry.revoke_trader(trader.address, sender=verifier)

    def test_revoke_fails_not_verified(self, trader_registry, deployer, trader):
        """Test cannot revoke non-verified trader"""
        with pytest.raises(Exception):
            trader_registry.revoke_trader(trader.address, sender=deployer)


class TestVerifierManagement:

    def test_add_verifier(self, trader_registry, deployer, verifier):
        """Test admin can add verifiers"""
        assert trader_registry.verifiers(verifier.address) == False

        trader_registry.add_verifier(verifier.address, sender=deployer)

        assert trader_registry.verifiers(verifier.address) == True

    def test_add_verifier_fails_non_admin(self, trader_registry, other_user, verifier):
        """Test non-admin cannot add verifiers"""
        with pytest.raises(Exception):
            trader_registry.add_verifier(verifier.address, sender=other_user)

    def test_add_verifier_fails_zero_address(self, trader_registry, deployer):
        """Test cannot add zero address as verifier"""
        with pytest.raises(Exception):
            trader_registry.add_verifier(
                "0x0000000000000000000000000000000000000000",
                sender=deployer
            )

    def test_remove_verifier(self, trader_registry, deployer, verifier):
        """Test admin can remove verifiers"""
        trader_registry.add_verifier(verifier.address, sender=deployer)
        assert trader_registry.verifiers(verifier.address) == True

        trader_registry.remove_verifier(verifier.address, sender=deployer)

        assert trader_registry.verifiers(verifier.address) == False

    def test_remove_verifier_fails_non_admin(self, trader_registry, deployer, verifier, other_user):
        """Test non-admin cannot remove verifiers"""
        trader_registry.add_verifier(verifier.address, sender=deployer)

        with pytest.raises(Exception):
            trader_registry.remove_verifier(verifier.address, sender=other_user)

    def test_new_verifier_can_verify(self, trader_registry, deployer, verifier, trader, sample_kyc_data):
        """Test newly added verifier can verify traders"""
        trader_registry.add_verifier(verifier.address, sender=deployer)

        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        trader_registry.verify_trader(1, sender=verifier)

        assert trader_registry.verified_traders(trader.address) == True

    def test_removed_verifier_cannot_verify(self, trader_registry, deployer, verifier, trader, sample_kyc_data):
        """Test removed verifier cannot verify traders"""
        trader_registry.add_verifier(verifier.address, sender=deployer)
        trader_registry.remove_verifier(verifier.address, sender=deployer)

        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        with pytest.raises(Exception):
            trader_registry.verify_trader(1, sender=verifier)


class TestGetters:

    def test_get_kyc(self, trader_registry, trader, sample_kyc_data):
        """Test get_kyc returns correct data"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        kyc = trader_registry.get_kyc(1)
        assert kyc.id == 1
        assert kyc.trader == trader.address
        assert kyc.full_name == sample_kyc_data["full_name"]

    def test_get_kyc_fails_invalid_id(self, trader_registry):
        """Test get_kyc fails with invalid ID"""
        with pytest.raises(Exception):
            trader_registry.get_kyc(999)

    def test_get_kyc_by_address(self, trader_registry, trader, sample_kyc_data):
        """Test get_kyc_by_address returns correct data"""
        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        kyc = trader_registry.get_kyc_by_address(trader.address)
        assert kyc.id == 1
        assert kyc.trader == trader.address

    def test_get_kyc_by_address_fails_no_kyc(self, trader_registry, other_user):
        """Test get_kyc_by_address fails when no KYC exists"""
        with pytest.raises(Exception):
            trader_registry.get_kyc_by_address(other_user.address)

    def test_is_verified_trader(self, trader_registry, deployer, trader, sample_kyc_data):
        """Test is_verified_trader returns correct status"""
        assert trader_registry.is_verified_trader(trader.address) == False

        trader_registry.submit_kyc(
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["country"],
            sample_kyc_data["ipfs_id_document"],
            sample_kyc_data["ipfs_selfie"],
            sender=trader
        )

        assert trader_registry.is_verified_trader(trader.address) == False

        trader_registry.verify_trader(1, sender=deployer)

        assert trader_registry.is_verified_trader(trader.address) == True
