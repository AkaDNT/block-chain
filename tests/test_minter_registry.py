import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts.test_accounts[0]


@pytest.fixture
def requester():
    return accounts.test_accounts[1]


@pytest.fixture
def other_user():
    return accounts.test_accounts[2]


@pytest.fixture
def base_token(deployer):
    """Deploy BaseToken contract"""
    return deployer.deploy(project.BaseToken)


@pytest.fixture
def minter_registry(deployer, base_token):
    """Deploy MinterRegistry contract"""
    return deployer.deploy(project.MinterRegistry, base_token.address)


@pytest.fixture
def sample_kyc_data():
    """Sample KYC data for minter requests"""
    return {
        "reason": "Company wants to issue stock tokens for trading",
        "full_name": "John Doe",
        "email": "john.doe@company.com",
        "ipfs_id_front": "QmIdFrontCID123456789012345678901234567890123",
        "ipfs_id_back": "QmIdBackCID1234567890123456789012345678901234",
        "ipfs_selfie": "QmSelfieCID12345678901234567890123456789012345"
    }


class TestMinterRegistryDeployment:

    def test_deployment(self, minter_registry, deployer, base_token):
        """Test MinterRegistry deployment"""
        assert minter_registry.admin() == deployer.address
        assert minter_registry.base_token() == base_token.address
        assert minter_registry.request_count() == 0

    def test_admin_is_not_auto_approved(self, minter_registry, deployer):
        """Test that admin is not automatically an approved minter"""
        assert minter_registry.approved_minters(deployer.address) == False


class TestMinterRequest:

    def test_request_minter(self, minter_registry, requester, sample_kyc_data):
        """Test submitting a minter request"""
        tx = minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        # Check request count
        assert minter_registry.request_count() == 1

        # Check address mapping
        assert minter_registry.address_to_request(requester.address) == 1

        # Check request details
        request = minter_registry.get_request(1)
        assert request.id == 1
        assert request.requester == requester.address
        assert request.reason == sample_kyc_data["reason"]
        assert request.full_name == sample_kyc_data["full_name"]
        assert request.email == sample_kyc_data["email"]
        assert request.ipfs_id_front == sample_kyc_data["ipfs_id_front"]
        assert request.ipfs_id_back == sample_kyc_data["ipfs_id_back"]
        assert request.ipfs_selfie == sample_kyc_data["ipfs_selfie"]
        assert request.status == 1  # PENDING
        assert request.processed_by == "0x0000000000000000000000000000000000000000"

        # Check event
        events = tx.decode_logs(minter_registry.MinterRequested)
        assert len(events) == 1
        assert events[0].request_id == 1
        assert events[0].requester == requester.address

    def test_cannot_request_twice(self, minter_registry, requester, sample_kyc_data):
        """Test that same address cannot submit multiple requests"""
        # First request
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        # Second request should fail
        with pytest.raises(Exception):
            minter_registry.request_minter(
                "Another reason",
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_reason(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty reason"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                "",
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_full_name(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty full name"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                sample_kyc_data["reason"],
                "",
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_email(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty email"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                sample_kyc_data["reason"],
                sample_kyc_data["full_name"],
                "",
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_id_front(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty ID front photo"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                sample_kyc_data["reason"],
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                "",
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_id_back(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty ID back photo"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                sample_kyc_data["reason"],
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                "",
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )

    def test_request_fails_empty_selfie(self, minter_registry, requester, sample_kyc_data):
        """Test request fails with empty selfie photo"""
        with pytest.raises(Exception):
            minter_registry.request_minter(
                sample_kyc_data["reason"],
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                "",
                sender=requester
            )


class TestApproveRequest:

    def test_approve_request(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test admin can approve a minter request"""
        # Submit request
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        # Approve request
        tx = minter_registry.approve_request(1, sender=deployer)

        # Check request status
        request = minter_registry.get_request(1)
        assert request.status == 2  # APPROVED
        assert request.processed_by == deployer.address
        assert request.processed_at > 0

        # Check approved minter status
        assert minter_registry.approved_minters(requester.address) == True
        assert minter_registry.is_approved_minter(requester.address) == True

        # Check event
        events = tx.decode_logs(minter_registry.MinterApproved)
        assert len(events) == 1
        assert events[0].request_id == 1
        assert events[0].requester == requester.address
        assert events[0].approved_by == deployer.address

    def test_approve_fails_non_admin(self, minter_registry, requester, other_user, sample_kyc_data):
        """Test non-admin cannot approve requests"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        with pytest.raises(Exception):
            minter_registry.approve_request(1, sender=other_user)

    def test_approve_fails_invalid_request_id(self, minter_registry, deployer):
        """Test approve fails with invalid request ID"""
        with pytest.raises(Exception):
            minter_registry.approve_request(999, sender=deployer)

    def test_approve_fails_already_approved(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test cannot approve already approved request"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        minter_registry.approve_request(1, sender=deployer)

        with pytest.raises(Exception):
            minter_registry.approve_request(1, sender=deployer)

    def test_approved_minter_cannot_request_again(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test approved minter cannot submit new request"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        minter_registry.approve_request(1, sender=deployer)

        with pytest.raises(Exception):
            minter_registry.request_minter(
                "New reason",
                sample_kyc_data["full_name"],
                sample_kyc_data["email"],
                sample_kyc_data["ipfs_id_front"],
                sample_kyc_data["ipfs_id_back"],
                sample_kyc_data["ipfs_selfie"],
                sender=requester
            )


class TestRejectRequest:

    def test_reject_request(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test admin can reject a minter request"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        rejection_reason = "Insufficient documentation provided"
        tx = minter_registry.reject_request(1, rejection_reason, sender=deployer)

        # Check request status
        request = minter_registry.get_request(1)
        assert request.status == 4  # REJECTED
        assert request.processed_by == deployer.address
        assert request.rejection_reason == rejection_reason

        # Check not approved
        assert minter_registry.approved_minters(requester.address) == False

        # Check address mapping cleared (allows re-application)
        assert minter_registry.address_to_request(requester.address) == 0

        # Check event
        events = tx.decode_logs(minter_registry.MinterRejected)
        assert len(events) == 1
        assert events[0].request_id == 1
        assert events[0].requester == requester.address
        assert events[0].rejected_by == deployer.address
        assert events[0].rejection_reason == rejection_reason

    def test_reject_fails_non_admin(self, minter_registry, requester, other_user, sample_kyc_data):
        """Test non-admin cannot reject requests"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        with pytest.raises(Exception):
            minter_registry.reject_request(1, "Rejected", sender=other_user)

    def test_reject_fails_empty_reason(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test reject fails with empty rejection reason"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        with pytest.raises(Exception):
            minter_registry.reject_request(1, "", sender=deployer)

    def test_can_reapply_after_rejection(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test user can reapply after rejection"""
        # First request
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        # Reject
        minter_registry.reject_request(1, "Insufficient docs", sender=deployer)

        # Reapply
        minter_registry.request_minter(
            "Updated reason with better documentation",
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            "QmNewIdFrontCID12345678901234567890123456789",
            "QmNewIdBackCID123456789012345678901234567890",
            "QmNewSelfieCID1234567890123456789012345678901",
            sender=requester
        )

        assert minter_registry.request_count() == 2
        assert minter_registry.address_to_request(requester.address) == 2


class TestRevokeMinter:

    def test_revoke_minter(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test admin can revoke minter privileges"""
        # Submit and approve request
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )
        minter_registry.approve_request(1, sender=deployer)

        # Revoke minter
        tx = minter_registry.revoke_minter(requester.address, sender=deployer)

        # Check status
        request = minter_registry.get_request(1)
        assert request.status == 8  # REVOKED
        assert minter_registry.approved_minters(requester.address) == False

        # Check event
        events = tx.decode_logs(minter_registry.MinterRevoked)
        assert len(events) == 1
        assert events[0].minter == requester.address
        assert events[0].revoked_by == deployer.address

    def test_revoke_fails_non_admin(self, minter_registry, deployer, requester, other_user, sample_kyc_data):
        """Test non-admin cannot revoke minters"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )
        minter_registry.approve_request(1, sender=deployer)

        with pytest.raises(Exception):
            minter_registry.revoke_minter(requester.address, sender=other_user)

    def test_revoke_fails_not_approved(self, minter_registry, deployer, requester):
        """Test cannot revoke non-approved minter"""
        with pytest.raises(Exception):
            minter_registry.revoke_minter(requester.address, sender=deployer)


class TestGetters:

    def test_get_request(self, minter_registry, requester, sample_kyc_data):
        """Test get_request returns correct data"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        request = minter_registry.get_request(1)
        assert request.id == 1
        assert request.requester == requester.address

    def test_get_request_fails_invalid_id(self, minter_registry):
        """Test get_request fails with invalid ID"""
        with pytest.raises(Exception):
            minter_registry.get_request(999)

    def test_get_request_by_address(self, minter_registry, requester, sample_kyc_data):
        """Test get_request_by_address returns correct data"""
        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        request = minter_registry.get_request_by_address(requester.address)
        assert request.id == 1
        assert request.requester == requester.address

    def test_get_request_by_address_fails_no_request(self, minter_registry, other_user):
        """Test get_request_by_address fails when no request exists"""
        with pytest.raises(Exception):
            minter_registry.get_request_by_address(other_user.address)

    def test_is_approved_minter(self, minter_registry, deployer, requester, sample_kyc_data):
        """Test is_approved_minter returns correct status"""
        assert minter_registry.is_approved_minter(requester.address) == False

        minter_registry.request_minter(
            sample_kyc_data["reason"],
            sample_kyc_data["full_name"],
            sample_kyc_data["email"],
            sample_kyc_data["ipfs_id_front"],
            sample_kyc_data["ipfs_id_back"],
            sample_kyc_data["ipfs_selfie"],
            sender=requester
        )

        assert minter_registry.is_approved_minter(requester.address) == False

        minter_registry.approve_request(1, sender=deployer)

        assert minter_registry.is_approved_minter(requester.address) == True
