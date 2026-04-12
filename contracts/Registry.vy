# @version 0.4.3
"""
@title Company Registry
@author Stock Trading System
@notice Registry for managing company registrations and verification
"""

# Events
event CompanyRegistered:
    company_id: indexed(uint256)
    owner: indexed(address)
    name: String[128]
    symbol: String[32]
    ipfs_prospectus: String[64]
    ipfs_financials: String[64]
    ipfs_logo: String[64]

event CompanyVerified:
    company_id: indexed(uint256)
    verified_by: indexed(address)

event IPFSUpdated:
    company_id: indexed(uint256)
    document_type: String[32]
    old_cid: String[64]
    new_cid: String[64]

# Structs
struct Company:
    id: uint256
    owner: address
    name: String[128]
    symbol: String[32]
    ipfs_prospectus: String[64]
    ipfs_financials: String[64]
    ipfs_logo: String[64]
    is_verified: bool
    stock_token: address
    amm_pool: address
    created_at: uint256

# State variables
companies: public(HashMap[uint256, Company])
company_count: public(uint256)
owner_to_company: public(HashMap[address, uint256])
symbol_to_company: public(HashMap[String[32], uint256])

# Admin controls
admin: public(address)
verifiers: public(HashMap[address, bool])

@deploy
def __init__():
    """
    @notice Initialize the registry
    """
    self.admin = msg.sender
    self.verifiers[msg.sender] = True
    self.company_count = 0

@external
def register_company(
    _name: String[128],
    _symbol: String[32],
    _ipfs_prospectus: String[64],
    _ipfs_financials: String[64],
    _ipfs_logo: String[64]
) -> uint256:
    """
    @notice Register a new company
    @param _name Company name
    @param _symbol Company symbol (unique)
    @param _ipfs_prospectus IPFS CID for prospectus document
    @param _ipfs_financials IPFS CID for financial statements
    @param _ipfs_logo IPFS CID for company logo
    @return Company ID
    """
    assert len(_name) > 0, "Company name cannot be empty"
    assert len(_symbol) > 0, "Company symbol cannot be empty"
    assert len(_ipfs_prospectus) > 0, "Prospectus IPFS CID cannot be empty"
    assert self.owner_to_company[msg.sender] == 0, "Address already has a company"
    assert self.symbol_to_company[_symbol] == 0, "Symbol already taken"

    # Increment company count and create new company
    self.company_count += 1
    company_id: uint256 = self.company_count

    # Store company data
    self.companies[company_id] = Company({
        id: company_id,
        owner: msg.sender,
        name: _name,
        symbol: _symbol,
        ipfs_prospectus: _ipfs_prospectus,
        ipfs_financials: _ipfs_financials,
        ipfs_logo: _ipfs_logo,
        is_verified: False,
        stock_token: empty(address),
        amm_pool: empty(address),
        created_at: block.timestamp
    })

    # Update mappings
    self.owner_to_company[msg.sender] = company_id
    self.symbol_to_company[_symbol] = company_id

    log CompanyRegistered(company_id, msg.sender, _name, _symbol, _ipfs_prospectus, _ipfs_financials, _ipfs_logo)
    return company_id

@external
def set_verified(_company_id: uint256, _verified: bool):
    """
    @notice Set company verification status (only verifiers)
    @param _company_id Company ID
    @param _verified Verification status
    """
    assert self.verifiers[msg.sender], "Only verifiers can set verification"
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"

    self.companies[_company_id].is_verified = _verified

    if _verified:
        log CompanyVerified(_company_id, msg.sender)

@external
def update_ipfs_prospectus(_company_id: uint256, _new_cid: String[64]):
    """
    @notice Update company prospectus IPFS CID (only company owner)
    @param _company_id Company ID
    @param _new_cid New IPFS CID
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]
    assert msg.sender == company.owner, "Only company owner can update CID"
    assert len(_new_cid) > 0, "IPFS CID cannot be empty"

    old_cid: String[64] = company.ipfs_prospectus
    self.companies[_company_id].ipfs_prospectus = _new_cid

    log IPFSUpdated(_company_id, "prospectus", old_cid, _new_cid)

@external
def update_ipfs_financials(_company_id: uint256, _new_cid: String[64]):
    """
    @notice Update company financials IPFS CID (only company owner)
    @param _company_id Company ID
    @param _new_cid New IPFS CID
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]
    assert msg.sender == company.owner, "Only company owner can update CID"
    assert len(_new_cid) > 0, "IPFS CID cannot be empty"

    old_cid: String[64] = company.ipfs_financials
    self.companies[_company_id].ipfs_financials = _new_cid

    log IPFSUpdated(_company_id, "financials", old_cid, _new_cid)

@external
def update_ipfs_logo(_company_id: uint256, _new_cid: String[64]):
    """
    @notice Update company logo IPFS CID (only company owner)
    @param _company_id Company ID
    @param _new_cid New IPFS CID
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]
    assert msg.sender == company.owner, "Only company owner can update CID"
    assert len(_new_cid) > 0, "IPFS CID cannot be empty"

    old_cid: String[64] = company.ipfs_logo
    self.companies[_company_id].ipfs_logo = _new_cid

    log IPFSUpdated(_company_id, "logo", old_cid, _new_cid)

@external
def set_stock_token(_company_id: uint256, _token_address: address):
    """
    @notice Set stock token address for company (only company owner)
    @param _company_id Company ID
    @param _token_address Stock token contract address
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]
    assert msg.sender == company.owner, "Only company owner can set token"
    assert _token_address != empty(address), "Invalid token address"

    self.companies[_company_id].stock_token = _token_address

@external
def set_amm_pool(_company_id: uint256, _pool_address: address):
    """
    @notice Set AMM pool address for company (only company owner)
    @param _company_id Company ID
    @param _pool_address AMM pool contract address
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]
    assert msg.sender == company.owner, "Only company owner can set pool"
    assert _pool_address != empty(address), "Invalid pool address"

    self.companies[_company_id].amm_pool = _pool_address

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

@external
def remove_company(_company_id: uint256):
    """
    @notice Remove a company (only company owner or admin)
    @dev WARNING: This is for development/testing only. In production, companies should not be deletable.
    @param _company_id Company ID to remove
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    company: Company = self.companies[_company_id]

    # Only company owner or admin can remove
    assert msg.sender == company.owner or msg.sender == self.admin, "Only owner or admin can remove company"

    # Clear mappings
    self.owner_to_company[company.owner] = 0
    self.symbol_to_company[company.symbol] = 0

    # Clear company data (reset to empty struct)
    self.companies[_company_id] = Company({
        id: 0,
        owner: empty(address),
        name: "",
        symbol: "",
        ipfs_prospectus: "",
        ipfs_financials: "",
        ipfs_logo: "",
        is_verified: False,
        stock_token: empty(address),
        amm_pool: empty(address),
        created_at: 0
    })

@view
@external
def get_company(_company_id: uint256) -> Company:
    """
    @notice Get company information
    @param _company_id Company ID
    @return Company struct
    """
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company ID"
    return self.companies[_company_id]

@view
@external
def get_company_by_symbol(_symbol: String[32]) -> Company:
    """
    @notice Get company information by symbol
    @param _symbol Company symbol
    @return Company struct
    """
    company_id: uint256 = self.symbol_to_company[_symbol]
    assert company_id > 0, "Company not found"
    return self.companies[company_id]

@view
@external
def get_company_by_owner(_owner: address) -> Company:
    """
    @notice Get company information by owner address
    @param _owner Owner address
    @return Company struct
    """
    company_id: uint256 = self.owner_to_company[_owner]
    assert company_id > 0, "Company not found"
    return self.companies[company_id]
