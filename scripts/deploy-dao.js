const fs = require("fs");
const path = require("path");
const { ethers } = require("hardhat");

async function main() {
  const [deployer, memberOne, memberTwo, treasuryRecipient] = await ethers.getSigners();

  const initialSupply = ethers.parseUnits("10000", 18);
  const GovernanceToken = await ethers.getContractFactory("GovernanceToken");
  const token = await GovernanceToken.deploy("Community Governance Token", "CGT", initialSupply);
  await token.waitForDeployment();

  const MembershipNFT = await ethers.getContractFactory("MembershipNFT");
  const nft = await MembershipNFT.deploy("Community DAO Membership", "CDM");
  await nft.waitForDeployment();

  const quorumPercent = 20;
  const votingPeriod = 5 * 60;
  const CommunityDAO = await ethers.getContractFactory("CommunityDAO");
  const dao = await CommunityDAO.deploy(await token.getAddress(), await nft.getAddress(), quorumPercent, votingPeriod, {
    value: ethers.parseEther("3")
  });
  await dao.waitForDeployment();

  await (await token.transfer(memberOne.address, ethers.parseUnits("3000", 18))).wait();
  await (await token.transfer(memberTwo.address, ethers.parseUnits("2000", 18))).wait();
  await (await nft.mint(deployer.address)).wait();
  await (await nft.mint(memberOne.address)).wait();
  await (await nft.mint(memberTwo.address)).wait();

  const deployment = {
    network: hre.network.name,
    chainId: Number((await ethers.provider.getNetwork()).chainId),
    deployedAt: new Date().toISOString(),
    contracts: {
      GovernanceToken: await token.getAddress(),
      MembershipNFT: await nft.getAddress(),
      CommunityDAO: await dao.getAddress()
    },
    demoAccounts: {
      deployer: deployer.address,
      memberOne: memberOne.address,
      memberTwo: memberTwo.address,
      treasuryRecipient: treasuryRecipient.address
    },
    daoRules: {
      quorumPercent,
      votingPeriodSeconds: votingPeriod,
      votingModel: "1 ERC-20 token = 1 weighted vote; only NFT members can propose"
    }
  };

  const frontendPublic = path.join(__dirname, "..", "frontend", "public");
  fs.mkdirSync(frontendPublic, { recursive: true });
  fs.writeFileSync(path.join(frontendPublic, "deployment.json"), JSON.stringify(deployment, null, 2));
  fs.writeFileSync(path.join(__dirname, "..", "deployment.json"), JSON.stringify(deployment, null, 2));

  console.log("DAO deployment complete");
  console.log(JSON.stringify(deployment, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
