# @version 0.4.3
"""
@title Trader Registry
@author Stock Trading System
@notice Registry for managing individual trader verification (simplified KYC)
@dev Traders get verified to trade, but do NOT get minting privileges
"""

# Events
event TraderRegistered:
    trader: indexed(address)
    request_id: indexed(uint256)
    full_name: String[128]

event TraderVerified:
    trader: indexed(address)
    verified_by: indexed(address)
    request_id: indexed(uint256)

event TraderRejected:
    trader: indexed(address)
    rejected_by: indexed(address)
    request_id: indexed(uint256)
    rejection_reason: String[256]

event TraderRevoked:
    trader: indexed(address)
    revoked_by: indexed(address)

# Enums
enum VerificationStatus:
    PENDING
    VERIFIED
    REJECTED
    REVOKED

# Structs
struct TraderKYC:
    id: uint256
    trader: address
    full_name: String[128]
    email: String[128]
    country: String[64]
    ipfs_id_document: String[64]  # ID card or passport
    ipfs_selfie: String[64]       # Selfie with ID
    status: VerificationStatus
    created_at: uint256
    verified_at: uint256
    verified_by: address
    rejection_reason: String[256]

# State variables
kyc_requests: public(HashMap[uint256, TraderKYC])
kyc_count: public(uint256)
address_to_kyc: public(HashMap[address, uint256])
verified_traders: public(HashMap[address, bool])

# Admin controls
admin: public(address)
verifiers: public(HashMap[address, bool])

@deploy
def __init__():
    """
    @notice Initialize the trader registry
    """
    self.admin = msg.sender
    self.verifiers[msg.sender] = True
    self.kyc_count = 0

@external
def submit_kyc(
    _full_name: String[128],
    _email: String[128],
    _country: String[64],
    _ipfs_id_document: String[64],
    _ipfs_selfie: String[64]
) -> uint256:
    """
    @notice Submit KYC for trader verification
    @param _full_name Full legal name
    @param _email Email address
    @param _country Country of residence
    @param _ipfs_id_document IPFS CID for ID document
    @param _ipfs_selfie IPFS CID for selfie with ID
    @return KYC request ID
    """
    assert len(_full_name) > 0, "Full name cannot be empty"
    assert len(_email) > 0, "Email cannot be empty"
    assert len(_country) > 0, "Country cannot be empty"
    assert len(_ipfs_id_document) > 0, "ID document required"
    assert len(_ipfs_selfie) > 0, "Selfie required"
    assert self.address_to_kyc[msg.sender] == 0, "Already has a KYC request"
    assert not self.verified_traders[msg.sender], "Already verified"

    # Increment KYC count
    self.kyc_count += 1
    kyc_id: uint256 = self.kyc_count

    # Store KYC data
    self.kyc_requests[kyc_id] = TraderKYC({
        id: kyc_id,
        trader: msg.sender,
        full_name: _full_name,
        email: _email,
        country: _country,
        ipfs_id_document: _ipfs_id_document,
        ipfs_selfie: _ipfs_selfie,
        status: VerificationStatus.PENDING,
        created_at: block.timestamp,
        verified_at: 0,
        verified_by: empty(address),
        rejection_reason: ""
    })

    # Update mapping
    self.address_to_kyc[msg.sender] = kyc_id

    log TraderRegistered(msg.sender, kyc_id, _full_name)
    return kyc_id

@external
def verify_trader(_kyc_id: uint256):
    """
    @notice Verify a trader's KYC (only admin/verifiers)
    @param _kyc_id KYC request ID
    """
    assert self.verifiers[msg.sender], "Only verifiers can verify traders"
    assert _kyc_id > 0 and _kyc_id <= self.kyc_count, "Invalid KYC ID"

    kyc: TraderKYC = self.kyc_requests[_kyc_id]
    assert kyc.status == VerificationStatus.PENDING, "KYC is not pending"

    # Update KYC status
    self.kyc_requests[_kyc_id].status = VerificationStatus.VERIFIED
    self.kyc_requests[_kyc_id].verified_at = block.timestamp
    self.kyc_requests[_kyc_id].verified_by = msg.sender

    # Mark as verified trader
    self.verified_traders[kyc.trader] = True

    log TraderVerified(kyc.trader, msg.sender, _kyc_id)

@external
def reject_trader(_kyc_id: uint256, _rejection_reason: String[256]):
    """
    @notice Reject a trader's KYC (only admin/verifiers)
    @param _kyc_id KYC request ID
    @param _rejection_reason Reason for rejection
    """
    assert self.verifiers[msg.sender], "Only verifiers can reject traders"
    assert _kyc_id > 0 and _kyc_id <= self.kyc_count, "Invalid KYC ID"
    assert len(_rejection_reason) > 0, "Rejection reason cannot be empty"

    kyc: TraderKYC = self.kyc_requests[_kyc_id]
    assert kyc.status == VerificationStatus.PENDING, "KYC is not pending"

    # Update KYC status
    self.kyc_requests[_kyc_id].status = VerificationStatus.REJECTED
    self.kyc_requests[_kyc_id].verified_at = block.timestamp
    self.kyc_requests[_kyc_id].verified_by = msg.sender
    self.kyc_requests[_kyc_id].rejection_reason = _rejection_reason

    # Clear address mapping to allow re-submission
    self.address_to_kyc[kyc.trader] = 0

    log TraderRejected(kyc.trader, msg.sender, _kyc_id, _rejection_reason)

@external
def revoke_trader(_trader: address):
    """
    @notice Revoke trader verification (only admin)
    @param _trader Address to revoke
    """
    assert msg.sender == self.admin, "Only admin can revoke traders"
    assert self.verified_traders[_trader], "Address is not a verified trader"

    kyc_id: uint256 = self.address_to_kyc[_trader]

    # Update KYC status
    self.kyc_requests[kyc_id].status = VerificationStatus.REVOKED

    # Remove from verified traders
    self.verified_traders[_trader] = False

    log TraderRevoked(_trader, msg.sender)

@external
def add_verifier(_verifier: address):
    """
    @notice Add a new verifier (only admin)
    @param _verifier Address to add as verifier
    """
    assert msg.sender == self.admin, "Only admin can add verifiers"
    assert _verifier != empty(address), "Invalid verifier address"
    self.verifiers[_verifier] = True

@external
def remove_verifier(_verifier: address):
    """
    @notice Remove a verifier (only admin)
    @param _verifier Address to remove as verifier
    """
    assert msg.sender == self.admin, "Only admin can remove verifiers"
    self.verifiers[_verifier] = False

@view
@external
def get_kyc(_kyc_id: uint256) -> TraderKYC:
    """
    @notice Get KYC request information
    @param _kyc_id KYC request ID
    @return TraderKYC struct
    """
    assert _kyc_id > 0 and _kyc_id <= self.kyc_count, "Invalid KYC ID"
    return self.kyc_requests[_kyc_id]

@view
@external
def get_kyc_by_address(_trader: address) -> TraderKYC:
    """
    @notice Get KYC request by trader address
    @param _trader Trader address
    @return TraderKYC struct
    """
    kyc_id: uint256 = self.address_to_kyc[_trader]
    assert kyc_id > 0, "No KYC found for this address"
    return self.kyc_requests[kyc_id]

@view
@external
def is_verified_trader(_address: address) -> bool:
    """
    @notice Check if an address is a verified trader
    @param _address Address to check
    @return True if verified trader
    """
    return self.verified_traders[_address]
