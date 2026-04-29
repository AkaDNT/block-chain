const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CommunityDAO", function () {
  async function deployFixture() {
    const [owner, alice, bob, recipient] = await ethers.getSigners();

    const Token = await ethers.getContractFactory("GovernanceToken");
    const token = await Token.deploy("Community Governance Token", "CGT", ethers.parseUnits("1000", 18));

    const NFT = await ethers.getContractFactory("MembershipNFT");
    const nft = await NFT.deploy("Community DAO Membership", "CDM");

    const DAO = await ethers.getContractFactory("CommunityDAO");
    const dao = await DAO.deploy(await token.getAddress(), await nft.getAddress(), 20, 60, {
      value: ethers.parseEther("2")
    });

    await token.transfer(alice.address, ethers.parseUnits("300", 18));
    await token.transfer(bob.address, ethers.parseUnits("100", 18));
    await nft.mint(owner.address);
    await nft.mint(alice.address);

    return { owner, alice, bob, recipient, token, nft, dao };
  }

  it("requires an NFT membership card to create proposals", async function () {
    const { bob, recipient, dao } = await deployFixture();

    await expect(
      dao.connect(bob).propose(
        recipient.address,
        ethers.parseEther("1"),
        "Buy lab equipment",
        "Spend treasury funds on club equipment",
        "bafy-doc",
        "bafy-report",
        "bafy-rules"
      )
    ).to.be.revertedWith("MEMBERSHIP_REQUIRED");
  });

  it("passes a proposal only after quorum, majority, and voting deadline", async function () {
    const { alice, recipient, dao } = await deployFixture();

    await dao.connect(alice).propose(
      recipient.address,
      ethers.parseEther("1"),
      "Buy lab equipment",
      "Spend treasury funds on club equipment",
      "bafy-doc",
      "bafy-report",
      "bafy-rules"
    );

    await dao.connect(alice).vote(1, true);
    await expect(dao.execute(1)).to.be.revertedWith("VOTING_STILL_ACTIVE");

    await ethers.provider.send("evm_increaseTime", [61]);
    await ethers.provider.send("evm_mine");

    await expect(() => dao.execute(1)).to.changeEtherBalances(
      [dao, recipient],
      [ethers.parseEther("-1"), ethers.parseEther("1")]
    );
  });
});
