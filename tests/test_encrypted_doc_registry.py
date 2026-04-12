import pytest
from ape import accounts, project


@pytest.fixture
def deployer():
    return accounts.test_accounts[0]


@pytest.fixture
def uploader():
    return accounts.test_accounts[1]


@pytest.fixture
def recipient1():
    return accounts.test_accounts[2]


@pytest.fixture
def recipient2():
    return accounts.test_accounts[3]


@pytest.fixture
def other_user():
    return accounts.test_accounts[4]


@pytest.fixture
def doc_registry(deployer):
    """Deploy EncryptedDocRegistry contract"""
    return deployer.deploy(project.EncryptedDocRegistry)


@pytest.fixture
def sample_document():
    """Sample document data"""
    return {
        "cid": "QmDocumentCID123456789012345678901234567890123456",
        "doc_type": "kyc",
        "original_name": "identity_document.pdf",
        "original_size": 1024000,
        "company_id": 1
    }


@pytest.fixture
def sample_encrypted_key():
    """Sample encrypted key data"""
    return {
        "ephemeral_public_key": "0x04abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678",
        "iv": "0x1234567890abcdef12345678",
        "ciphertext": "0xencryptedaeskey1234567890abcdef1234567890abcdef1234567890abcdef",
        "mac": "0xmac1234567890abcdef1234567890abcdef1234567890abcdef1234567890ab"
    }


class TestEncryptedDocRegistryDeployment:

    def test_deployment(self, doc_registry, deployer):
        """Test EncryptedDocRegistry deployment"""
        assert doc_registry.admin() == deployer.address
        assert doc_registry.document_count() == 0


class TestUploadDocument:

    def test_upload_document(self, doc_registry, uploader, sample_document):
        """Test uploading an encrypted document"""
        tx = doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        # Check document count
        assert doc_registry.document_count() == 1

        # Check uploader document count
        assert doc_registry.uploader_doc_count(uploader.address) == 1

        # Check document details
        doc = doc_registry.get_document(1)
        assert doc.id == 1
        assert doc.uploader == uploader.address
        assert doc.cid == sample_document["cid"]
        assert doc.doc_type == sample_document["doc_type"]
        assert doc.original_name == sample_document["original_name"]
        assert doc.original_size == sample_document["original_size"]
        assert doc.company_id == sample_document["company_id"]
        assert doc.is_revoked == False
        assert doc.uploaded_at > 0

        # Check event
        events = tx.decode_logs(doc_registry.DocumentUploaded)
        assert len(events) == 1
        assert events[0].doc_id == 1
        assert events[0].uploader == uploader.address
        assert events[0].cid == sample_document["cid"]
        assert events[0].doc_type == sample_document["doc_type"]

    def test_upload_multiple_documents(self, doc_registry, uploader, sample_document):
        """Test uploading multiple documents"""
        # Upload first document
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        # Upload second document
        doc_registry.upload_document(
            "QmSecondDocCID12345678901234567890123456789012345",
            "financial",
            "financial_report.pdf",
            2048000,
            2,
            sender=uploader
        )

        assert doc_registry.document_count() == 2
        assert doc_registry.uploader_doc_count(uploader.address) == 2

    def test_upload_fails_empty_cid(self, doc_registry, uploader, sample_document):
        """Test upload fails with empty CID"""
        with pytest.raises(Exception):
            doc_registry.upload_document(
                "",
                sample_document["doc_type"],
                sample_document["original_name"],
                sample_document["original_size"],
                sample_document["company_id"],
                sender=uploader
            )

    def test_upload_with_zero_company_id(self, doc_registry, uploader, sample_document):
        """Test upload with zero company ID (no company association)"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            0,  # No company association
            sender=uploader
        )

        doc = doc_registry.get_document(1)
        assert doc.company_id == 0


class TestAddRecipient:

    def test_add_recipient(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test adding a recipient with encrypted key"""
        # Upload document
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        # Add recipient
        tx = doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        # Check recipient count
        assert doc_registry.recipient_count(1) == 1
        assert doc_registry.recipient_accessible_count(recipient1.address) == 1

        # Check encrypted key
        key = doc_registry.get_encrypted_key(1, recipient1.address)
        assert key.ephemeral_public_key == sample_encrypted_key["ephemeral_public_key"]
        assert key.iv == sample_encrypted_key["iv"]
        assert key.ciphertext == sample_encrypted_key["ciphertext"]
        assert key.mac == sample_encrypted_key["mac"]

        # Check can_access
        assert doc_registry.can_access(1, recipient1.address) == True

        # Check event
        events = tx.decode_logs(doc_registry.RecipientAdded)
        assert len(events) == 1
        assert events[0].doc_id == 1
        assert events[0].recipient == recipient1.address

    def test_add_multiple_recipients(self, doc_registry, uploader, recipient1, recipient2, sample_document, sample_encrypted_key):
        """Test adding multiple recipients"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        # Add first recipient
        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        # Add second recipient
        doc_registry.add_recipient(
            1,
            recipient2.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            "0xdifferentciphertext1234567890abcdef1234567890abcdef1234567890ab",
            sample_encrypted_key["mac"],
            sender=uploader
        )

        assert doc_registry.recipient_count(1) == 2
        assert doc_registry.can_access(1, recipient1.address) == True
        assert doc_registry.can_access(1, recipient2.address) == True

    def test_add_recipient_fails_non_uploader(self, doc_registry, uploader, recipient1, other_user, sample_document, sample_encrypted_key):
        """Test non-uploader cannot add recipients"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        with pytest.raises(Exception):
            doc_registry.add_recipient(
                1,
                recipient1.address,
                sample_encrypted_key["ephemeral_public_key"],
                sample_encrypted_key["iv"],
                sample_encrypted_key["ciphertext"],
                sample_encrypted_key["mac"],
                sender=other_user
            )

    def test_admin_can_add_recipient(self, doc_registry, deployer, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test admin can add recipients"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=deployer  # Admin
        )

        assert doc_registry.can_access(1, recipient1.address) == True

    def test_add_recipient_fails_invalid_doc_id(self, doc_registry, uploader, recipient1, sample_encrypted_key):
        """Test add recipient fails with invalid document ID"""
        with pytest.raises(Exception):
            doc_registry.add_recipient(
                999,
                recipient1.address,
                sample_encrypted_key["ephemeral_public_key"],
                sample_encrypted_key["iv"],
                sample_encrypted_key["ciphertext"],
                sample_encrypted_key["mac"],
                sender=uploader
            )

    def test_add_recipient_fails_zero_address(self, doc_registry, uploader, sample_document, sample_encrypted_key):
        """Test add recipient fails with zero address"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        with pytest.raises(Exception):
            doc_registry.add_recipient(
                1,
                "0x0000000000000000000000000000000000000000",
                sample_encrypted_key["ephemeral_public_key"],
                sample_encrypted_key["iv"],
                sample_encrypted_key["ciphertext"],
                sample_encrypted_key["mac"],
                sender=uploader
            )

    def test_add_recipient_fails_revoked_document(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test cannot add recipient to revoked document"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.revoke_document(1, sender=uploader)

        with pytest.raises(Exception):
            doc_registry.add_recipient(
                1,
                recipient1.address,
                sample_encrypted_key["ephemeral_public_key"],
                sample_encrypted_key["iv"],
                sample_encrypted_key["ciphertext"],
                sample_encrypted_key["mac"],
                sender=uploader
            )


class TestAddRecipientsBatch:

    def test_add_recipients_batch(self, doc_registry, uploader, recipient1, recipient2, sample_document, sample_encrypted_key):
        """Test adding multiple recipients in batch"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        recipients = [recipient1.address, recipient2.address]
        ephemeral_keys = [sample_encrypted_key["ephemeral_public_key"]] * 2
        ivs = [sample_encrypted_key["iv"]] * 2
        ciphertexts = [sample_encrypted_key["ciphertext"], "0xdifferentciphertext12345678901234567890abcdef1234567890abcdef12"]
        macs = [sample_encrypted_key["mac"]] * 2

        tx = doc_registry.add_recipients_batch(
            1,
            recipients,
            ephemeral_keys,
            ivs,
            ciphertexts,
            macs,
            sender=uploader
        )

        assert doc_registry.recipient_count(1) == 2
        assert doc_registry.can_access(1, recipient1.address) == True
        assert doc_registry.can_access(1, recipient2.address) == True

        # Check events
        events = tx.decode_logs(doc_registry.RecipientAdded)
        assert len(events) == 2

    def test_batch_fails_array_length_mismatch(self, doc_registry, uploader, recipient1, recipient2, sample_document, sample_encrypted_key):
        """Test batch add fails with mismatched array lengths"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        recipients = [recipient1.address, recipient2.address]
        ephemeral_keys = [sample_encrypted_key["ephemeral_public_key"]]  # Only 1 key
        ivs = [sample_encrypted_key["iv"]] * 2
        ciphertexts = [sample_encrypted_key["ciphertext"]] * 2
        macs = [sample_encrypted_key["mac"]] * 2

        with pytest.raises(Exception):
            doc_registry.add_recipients_batch(
                1,
                recipients,
                ephemeral_keys,
                ivs,
                ciphertexts,
                macs,
                sender=uploader
            )


class TestRemoveRecipient:

    def test_remove_recipient(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test removing a recipient"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        assert doc_registry.can_access(1, recipient1.address) == True

        tx = doc_registry.remove_recipient(1, recipient1.address, sender=uploader)

        # Check access revoked
        assert doc_registry.can_access(1, recipient1.address) == False

        # Check event
        events = tx.decode_logs(doc_registry.RecipientRemoved)
        assert len(events) == 1
        assert events[0].doc_id == 1
        assert events[0].recipient == recipient1.address

    def test_remove_recipient_fails_non_uploader(self, doc_registry, uploader, recipient1, other_user, sample_document, sample_encrypted_key):
        """Test non-uploader cannot remove recipients"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        with pytest.raises(Exception):
            doc_registry.remove_recipient(1, recipient1.address, sender=other_user)

    def test_admin_can_remove_recipient(self, doc_registry, deployer, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test admin can remove recipients"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        doc_registry.remove_recipient(1, recipient1.address, sender=deployer)

        assert doc_registry.can_access(1, recipient1.address) == False


class TestRevokeDocument:

    def test_revoke_document(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test revoking a document"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        tx = doc_registry.revoke_document(1, sender=uploader)

        # Check document is revoked
        doc = doc_registry.get_document(1)
        assert doc.is_revoked == True

        # Check access is denied
        assert doc_registry.can_access(1, recipient1.address) == False

        # Check event
        events = tx.decode_logs(doc_registry.DocumentRevoked)
        assert len(events) == 1
        assert events[0].doc_id == 1
        assert events[0].revoked_by == uploader.address

    def test_revoke_fails_non_uploader(self, doc_registry, uploader, other_user, sample_document):
        """Test non-uploader cannot revoke document"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        with pytest.raises(Exception):
            doc_registry.revoke_document(1, sender=other_user)

    def test_admin_can_revoke_document(self, doc_registry, deployer, uploader, sample_document):
        """Test admin can revoke document"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.revoke_document(1, sender=deployer)

        doc = doc_registry.get_document(1)
        assert doc.is_revoked == True

    def test_revoke_fails_invalid_doc_id(self, doc_registry, uploader):
        """Test revoke fails with invalid document ID"""
        with pytest.raises(Exception):
            doc_registry.revoke_document(999, sender=uploader)


class TestGetters:

    def test_get_document(self, doc_registry, uploader, sample_document):
        """Test get_document returns correct data"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc = doc_registry.get_document(1)
        assert doc.id == 1
        assert doc.uploader == uploader.address
        assert doc.cid == sample_document["cid"]

    def test_get_document_fails_invalid_id(self, doc_registry):
        """Test get_document fails with invalid ID"""
        with pytest.raises(Exception):
            doc_registry.get_document(999)

    def test_get_encrypted_key(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test get_encrypted_key returns correct data"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        key = doc_registry.get_encrypted_key(1, recipient1.address)
        assert key.ciphertext == sample_encrypted_key["ciphertext"]

    def test_get_encrypted_key_fails_no_access(self, doc_registry, uploader, recipient1, sample_document):
        """Test get_encrypted_key fails when recipient has no access"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        with pytest.raises(Exception):
            doc_registry.get_encrypted_key(1, recipient1.address)

    def test_get_encrypted_key_fails_revoked_document(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test get_encrypted_key fails for revoked document"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        doc_registry.revoke_document(1, sender=uploader)

        with pytest.raises(Exception):
            doc_registry.get_encrypted_key(1, recipient1.address)

    def test_can_access(self, doc_registry, uploader, recipient1, other_user, sample_document, sample_encrypted_key):
        """Test can_access returns correct status"""
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        # No access before adding
        assert doc_registry.can_access(1, recipient1.address) == False
        assert doc_registry.can_access(1, other_user.address) == False

        # Add recipient
        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        # Has access after adding
        assert doc_registry.can_access(1, recipient1.address) == True
        assert doc_registry.can_access(1, other_user.address) == False

    def test_can_access_invalid_doc_id(self, doc_registry, recipient1):
        """Test can_access returns False for invalid document ID"""
        assert doc_registry.can_access(0, recipient1.address) == False
        assert doc_registry.can_access(999, recipient1.address) == False

    def test_get_uploader_documents(self, doc_registry, uploader, sample_document):
        """Test get_uploader_documents returns correct list"""
        # Upload multiple documents
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.upload_document(
            "QmSecondDocCID12345678901234567890123456789012345",
            "financial",
            "report.pdf",
            2048000,
            2,
            sender=uploader
        )

        docs = doc_registry.get_uploader_documents(uploader.address)
        assert len(docs) == 2
        assert 1 in docs
        assert 2 in docs

    def test_get_accessible_documents(self, doc_registry, uploader, recipient1, sample_document, sample_encrypted_key):
        """Test get_accessible_documents returns correct list"""
        # Upload and share document
        doc_registry.upload_document(
            sample_document["cid"],
            sample_document["doc_type"],
            sample_document["original_name"],
            sample_document["original_size"],
            sample_document["company_id"],
            sender=uploader
        )

        doc_registry.add_recipient(
            1,
            recipient1.address,
            sample_encrypted_key["ephemeral_public_key"],
            sample_encrypted_key["iv"],
            sample_encrypted_key["ciphertext"],
            sample_encrypted_key["mac"],
            sender=uploader
        )

        docs = doc_registry.get_accessible_documents(recipient1.address)
        assert len(docs) == 1
        assert 1 in docs


class TestTransferAdmin:

    def test_transfer_admin(self, doc_registry, deployer, other_user):
        """Test admin can transfer admin role"""
        doc_registry.transfer_admin(other_user.address, sender=deployer)

        assert doc_registry.admin() == other_user.address

    def test_transfer_admin_fails_non_admin(self, doc_registry, other_user, recipient1):
        """Test non-admin cannot transfer admin role"""
        with pytest.raises(Exception):
            doc_registry.transfer_admin(recipient1.address, sender=other_user)

    def test_transfer_admin_fails_zero_address(self, doc_registry, deployer):
        """Test cannot transfer admin to zero address"""
        with pytest.raises(Exception):
            doc_registry.transfer_admin(
                "0x0000000000000000000000000000000000000000",
                sender=deployer
            )
