# @version 0.4.3
"""
@title Encrypted Document Registry
@author Stock Trading System
@notice Registry for storing encrypted IPFS document metadata and access control keys
@dev Stores encrypted AES keys for each authorized recipient
"""

# Events
event DocumentUploaded:
    doc_id: indexed(uint256)
    uploader: indexed(address)
    cid: String[64]
    doc_type: String[32]

event RecipientAdded:
    doc_id: indexed(uint256)
    recipient: indexed(address)

event RecipientRemoved:
    doc_id: indexed(uint256)
    recipient: indexed(address)

event DocumentRevoked:
    doc_id: indexed(uint256)
    revoked_by: indexed(address)

# Structs
struct EncryptedKey:
    ephemeral_public_key: String[132]  # 0x04 + 64 bytes hex = 130 chars + buffer
    iv: String[32]                      # 12 bytes hex = 24 chars + buffer
    ciphertext: String[128]             # Encrypted AES key ~48 bytes hex
    mac: String[66]                     # keccak256 hash

struct DocumentMetadata:
    id: uint256
    uploader: address
    cid: String[64]                     # IPFS CID of encrypted file
    doc_type: String[32]                # e.g., "kyc", "prospectus", "financial"
    original_name: String[128]
    original_size: uint256
    uploaded_at: uint256
    is_revoked: bool
    company_id: uint256                 # Optional: link to company in Registry

# State variables
documents: public(HashMap[uint256, DocumentMetadata])
document_count: public(uint256)

# Mapping: doc_id => recipient => encrypted_key
encrypted_keys: public(HashMap[uint256, HashMap[address, EncryptedKey]])

# Mapping: doc_id => list of recipients (for enumeration)
doc_recipients: HashMap[uint256, DynArray[address, 100]]
recipient_count: public(HashMap[uint256, uint256])

# Mapping: uploader => their document IDs
uploader_documents: HashMap[address, DynArray[uint256, 1000]]
uploader_doc_count: public(HashMap[address, uint256])

# Mapping: recipient => documents they can access
recipient_documents: HashMap[address, DynArray[uint256, 1000]]
recipient_accessible_count: public(HashMap[address, uint256])

# Access control
admin: public(address)

@deploy
def __init__():
    """
    @notice Initialize the encrypted document registry
    """
    self.admin = msg.sender
    self.document_count = 0

@external
def upload_document(
    _cid: String[64],
    _doc_type: String[32],
    _original_name: String[128],
    _original_size: uint256,
    _company_id: uint256
) -> uint256:
    """
    @notice Register an encrypted document upload
    @param _cid IPFS CID of the encrypted file
    @param _doc_type Document type identifier
    @param _original_name Original filename
    @param _original_size Original file size in bytes
    @param _company_id Associated company ID (0 if none)
    @return Document ID
    """
    assert len(_cid) > 0, "CID cannot be empty"

    self.document_count += 1
    doc_id: uint256 = self.document_count

    self.documents[doc_id] = DocumentMetadata({
        id: doc_id,
        uploader: msg.sender,
        cid: _cid,
        doc_type: _doc_type,
        original_name: _original_name,
        original_size: _original_size,
        uploaded_at: block.timestamp,
        is_revoked: False,
        company_id: _company_id
    })

    # Track uploader's documents
    self.uploader_documents[msg.sender].append(doc_id)
    self.uploader_doc_count[msg.sender] += 1

    log DocumentUploaded(doc_id, msg.sender, _cid, _doc_type)
    return doc_id

@external
def add_recipient(
    _doc_id: uint256,
    _recipient: address,
    _ephemeral_public_key: String[132],
    _iv: String[32],
    _ciphertext: String[128],
    _mac: String[66]
):
    """
    @notice Add a recipient with their encrypted key
    @param _doc_id Document ID
    @param _recipient Recipient address
    @param _ephemeral_public_key ECIES ephemeral public key
    @param _iv Encryption IV
    @param _ciphertext Encrypted AES key
    @param _mac Message authentication code
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    doc: DocumentMetadata = self.documents[_doc_id]
    assert msg.sender == doc.uploader or msg.sender == self.admin, "Only uploader or admin"
    assert not doc.is_revoked, "Document is revoked"
    assert _recipient != empty(address), "Invalid recipient"

    # Store encrypted key
    self.encrypted_keys[_doc_id][_recipient] = EncryptedKey({
        ephemeral_public_key: _ephemeral_public_key,
        iv: _iv,
        ciphertext: _ciphertext,
        mac: _mac
    })

    # Track recipient
    self.doc_recipients[_doc_id].append(_recipient)
    self.recipient_count[_doc_id] += 1

    # Track accessible documents for recipient
    self.recipient_documents[_recipient].append(_doc_id)
    self.recipient_accessible_count[_recipient] += 1

    log RecipientAdded(_doc_id, _recipient)

@external
def add_recipients_batch(
    _doc_id: uint256,
    _recipients: DynArray[address, 20],
    _ephemeral_public_keys: DynArray[String[132], 20],
    _ivs: DynArray[String[32], 20],
    _ciphertexts: DynArray[String[128], 20],
    _macs: DynArray[String[66], 20]
):
    """
    @notice Add multiple recipients in a single transaction
    @dev All arrays must have the same length
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    doc: DocumentMetadata = self.documents[_doc_id]
    assert msg.sender == doc.uploader or msg.sender == self.admin, "Only uploader or admin"
    assert not doc.is_revoked, "Document is revoked"

    count: uint256 = len(_recipients)
    assert count == len(_ephemeral_public_keys), "Array length mismatch"
    assert count == len(_ivs), "Array length mismatch"
    assert count == len(_ciphertexts), "Array length mismatch"
    assert count == len(_macs), "Array length mismatch"

    for i: uint256 in range(20):
        if i >= count:
            break

        recipient: address = _recipients[i]
        assert recipient != empty(address), "Invalid recipient"

        self.encrypted_keys[_doc_id][recipient] = EncryptedKey({
            ephemeral_public_key: _ephemeral_public_keys[i],
            iv: _ivs[i],
            ciphertext: _ciphertexts[i],
            mac: _macs[i]
        })

        self.doc_recipients[_doc_id].append(recipient)
        self.recipient_count[_doc_id] += 1

        self.recipient_documents[recipient].append(_doc_id)
        self.recipient_accessible_count[recipient] += 1

        log RecipientAdded(_doc_id, recipient)

@external
def remove_recipient(_doc_id: uint256, _recipient: address):
    """
    @notice Remove a recipient's access (clears their encrypted key)
    @param _doc_id Document ID
    @param _recipient Recipient to remove
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    doc: DocumentMetadata = self.documents[_doc_id]
    assert msg.sender == doc.uploader or msg.sender == self.admin, "Only uploader or admin"

    # Clear encrypted key (recipient can no longer decrypt)
    self.encrypted_keys[_doc_id][_recipient] = EncryptedKey({
        ephemeral_public_key: "",
        iv: "",
        ciphertext: "",
        mac: ""
    })

    log RecipientRemoved(_doc_id, _recipient)

@external
def revoke_document(_doc_id: uint256):
    """
    @notice Revoke a document (marks as inaccessible)
    @dev Note: The encrypted file still exists on IPFS, but keys are invalidated
    @param _doc_id Document ID
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    doc: DocumentMetadata = self.documents[_doc_id]
    assert msg.sender == doc.uploader or msg.sender == self.admin, "Only uploader or admin"

    self.documents[_doc_id].is_revoked = True

    log DocumentRevoked(_doc_id, msg.sender)

@view
@external
def get_document(_doc_id: uint256) -> DocumentMetadata:
    """
    @notice Get document metadata
    @param _doc_id Document ID
    @return Document metadata
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    return self.documents[_doc_id]

@view
@external
def get_encrypted_key(_doc_id: uint256, _recipient: address) -> EncryptedKey:
    """
    @notice Get encrypted key for a recipient
    @param _doc_id Document ID
    @param _recipient Recipient address
    @return Encrypted key data
    """
    assert _doc_id > 0 and _doc_id <= self.document_count, "Invalid document ID"
    doc: DocumentMetadata = self.documents[_doc_id]
    assert not doc.is_revoked, "Document is revoked"

    key: EncryptedKey = self.encrypted_keys[_doc_id][_recipient]
    assert len(key.ciphertext) > 0, "No access for this recipient"

    return key

@view
@external
def can_access(_doc_id: uint256, _recipient: address) -> bool:
    """
    @notice Check if a recipient can access a document
    @param _doc_id Document ID
    @param _recipient Recipient address
    @return True if recipient has access
    """
    if _doc_id == 0 or _doc_id > self.document_count:
        return False

    doc: DocumentMetadata = self.documents[_doc_id]
    if doc.is_revoked:
        return False

    key: EncryptedKey = self.encrypted_keys[_doc_id][_recipient]
    return len(key.ciphertext) > 0

@view
@external
def get_uploader_documents(_uploader: address) -> DynArray[uint256, 1000]:
    """
    @notice Get all document IDs uploaded by an address
    @param _uploader Uploader address
    @return Array of document IDs
    """
    return self.uploader_documents[_uploader]

@view
@external
def get_accessible_documents(_recipient: address) -> DynArray[uint256, 1000]:
    """
    @notice Get all document IDs accessible by a recipient
    @param _recipient Recipient address
    @return Array of document IDs
    """
    return self.recipient_documents[_recipient]

@external
def transfer_admin(_new_admin: address):
    """
    @notice Transfer admin role
    @param _new_admin New admin address
    """
    assert msg.sender == self.admin, "Only admin"
    assert _new_admin != empty(address), "Invalid address"
    self.admin = _new_admin
