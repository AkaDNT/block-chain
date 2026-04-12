# @version 0.4.3
"""
@title Minter Registry (Company Verification)
@author Stock Trading System
@notice Registry for managing company minter requests with heavy KYC
@dev This is for COMPANIES who need to mint their own stock tokens, NOT for individual traders
     Individual traders should use TraderRegistry instead
"""

# Events
event MinterRequested:
    request_id: indexed(uint256)
    requester: indexed(address)
    reason: String[256]

event MinterApproved:
    request_id: indexed(uint256)
    requester: indexed(address)
    approved_by: indexed(address)

event MinterRejected:
    request_id: indexed(uint256)
    requester: indexed(address)
    rejected_by: indexed(address)
    rejection_reason: String[256]

event MinterRevoked:
    minter: indexed(address)
    revoked_by: indexed(address)

# Enums
enum RequestStatus:
    PENDING
    APPROVED
    REJECTED
    REVOKED

# Structs
struct MinterRequest:
    id: uint256
    requester: address
    reason: String[256]
    full_name: String[128]
    email: String[128]
    ipfs_id_front: String[64]
    ipfs_id_back: String[64]
    ipfs_selfie: String[64]
    status: RequestStatus
    created_at: uint256
    processed_at: uint256
    processed_by: address
    rejection_reason: String[256]

# State variables
requests: public(HashMap[uint256, MinterRequest])
request_count: public(uint256)
address_to_request: public(HashMap[address, uint256])
approved_minters: public(HashMap[address, bool])

# Admin controls
admin: public(address)
base_token: public(address)

@deploy
def __init__(_base_token: address):
    """
    @notice Initialize the minter registry
    @param _base_token Address of the base token contract
    """
    self.admin = msg.sender
    self.base_token = _base_token
    self.request_count = 0

@external
def request_minter(
    _reason: String[256],
    _full_name: String[128],
    _email: String[128],
    _ipfs_id_front: String[64],
    _ipfs_id_back: String[64],
    _ipfs_selfie: String[64]
) -> uint256:
    """
    @notice Request minter privileges with KYC information
    @param _reason Reason for requesting minter privileges
    @param _full_name Full legal name
    @param _email Email address
    @param _ipfs_id_front IPFS CID for ID front photo
    @param _ipfs_id_back IPFS CID for ID back photo
    @param _ipfs_selfie IPFS CID for selfie with ID
    @return Request ID
    """
    assert len(_reason) > 0, "Reason cannot be empty"
    assert len(_full_name) > 0, "Full name cannot be empty"
    assert len(_email) > 0, "Email cannot be empty"
    assert len(_ipfs_id_front) > 0, "ID front photo required"
    assert len(_ipfs_id_back) > 0, "ID back photo required"
    assert len(_ipfs_selfie) > 0, "Selfie photo required"
    assert self.address_to_request[msg.sender] == 0, "Already has a pending or approved request"
    assert not self.approved_minters[msg.sender], "Already an approved minter"

    # Increment request count
    self.request_count += 1
    request_id: uint256 = self.request_count

    # Store request data
    self.requests[request_id] = MinterRequest({
        id: request_id,
        requester: msg.sender,
        reason: _reason,
        full_name: _full_name,
        email: _email,
        ipfs_id_front: _ipfs_id_front,
        ipfs_id_back: _ipfs_id_back,
        ipfs_selfie: _ipfs_selfie,
        status: RequestStatus.PENDING,
        created_at: block.timestamp,
        processed_at: 0,
        processed_by: empty(address),
        rejection_reason: ""
    })

    # Update mapping
    self.address_to_request[msg.sender] = request_id

    log MinterRequested(request_id, msg.sender, _reason)
    return request_id

@external
def approve_request(_request_id: uint256):
    """
    @notice Approve a minter request (only admin)
    @param _request_id Request ID
    """
    assert msg.sender == self.admin, "Only admin can approve requests"
    assert _request_id > 0 and _request_id <= self.request_count, "Invalid request ID"

    request: MinterRequest = self.requests[_request_id]
    assert request.status == RequestStatus.PENDING, "Request is not pending"

    # Update request status
    self.requests[_request_id].status = RequestStatus.APPROVED
    self.requests[_request_id].processed_at = block.timestamp
    self.requests[_request_id].processed_by = msg.sender

    # Mark as approved minter
    self.approved_minters[request.requester] = True

    log MinterApproved(_request_id, request.requester, msg.sender)

@external
def reject_request(_request_id: uint256, _rejection_reason: String[256]):
    """
    @notice Reject a minter request (only admin)
    @param _request_id Request ID
    @param _rejection_reason Reason for rejection
    """
    assert msg.sender == self.admin, "Only admin can reject requests"
    assert _request_id > 0 and _request_id <= self.request_count, "Invalid request ID"
    assert len(_rejection_reason) > 0, "Rejection reason cannot be empty"

    request: MinterRequest = self.requests[_request_id]
    assert request.status == RequestStatus.PENDING, "Request is not pending"

    # Update request status
    self.requests[_request_id].status = RequestStatus.REJECTED
    self.requests[_request_id].processed_at = block.timestamp
    self.requests[_request_id].processed_by = msg.sender
    self.requests[_request_id].rejection_reason = _rejection_reason

    # Clear address mapping to allow re-application
    self.address_to_request[request.requester] = 0

    log MinterRejected(_request_id, request.requester, msg.sender, _rejection_reason)

@external
def revoke_minter(_minter: address):
    """
    @notice Revoke minter privileges (only admin)
    @param _minter Address to revoke
    """
    assert msg.sender == self.admin, "Only admin can revoke minters"
    assert self.approved_minters[_minter], "Address is not an approved minter"

    request_id: uint256 = self.address_to_request[_minter]

    # Update request status
    self.requests[request_id].status = RequestStatus.REVOKED

    # Remove from approved minters
    self.approved_minters[_minter] = False

    log MinterRevoked(_minter, msg.sender)

@view
@external
def get_request(_request_id: uint256) -> MinterRequest:
    """
    @notice Get minter request information
    @param _request_id Request ID
    @return MinterRequest struct
    """
    assert _request_id > 0 and _request_id <= self.request_count, "Invalid request ID"
    return self.requests[_request_id]

@view
@external
def get_request_by_address(_requester: address) -> MinterRequest:
    """
    @notice Get minter request by requester address
    @param _requester Requester address
    @return MinterRequest struct
    """
    request_id: uint256 = self.address_to_request[_requester]
    assert request_id > 0, "No request found for this address"
    return self.requests[request_id]

@view
@external
def is_approved_minter(_address: address) -> bool:
    """
    @notice Check if an address is an approved minter
    @param _address Address to check
    @return True if approved minter
    """
    return self.approved_minters[_address]
