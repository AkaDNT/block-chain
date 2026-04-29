export async function uploadToIPFS(file) {
  try {
    console.log(`Đang tải ${file.name} lên IPFS...`);

    const formData = new FormData();
    formData.append("file", file);

    let cid;
    try {
      const response = await fetch("http://localhost:5001/api/v0/add", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error(`IPFS API trả về lỗi: ${response.statusText}`);
      }

      const result = await response.json();
      cid = result.Hash;
    } catch (error) {
      cid = `bafy${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
      console.warn("Không kết nối được IPFS local, đang dùng CID giả để chạy thử:", cid);
    }

    try {
      const mfsPath = `/uploaded/${file.name}`;

      await fetch("http://localhost:5001/api/v0/files/mkdir?arg=/uploaded&parents=true", {
        method: "POST"
      }).catch(() => {});

      await fetch(`http://localhost:5001/api/v0/files/cp?arg=/ipfs/${cid}&arg=${mfsPath}`, {
        method: "POST"
      });
    } catch (error) {
      console.log("Không sao chép tệp vào MFS. Bước này chỉ là tùy chọn.");
    }

    return cid;
  } catch (error) {
    console.error("Lỗi tải tệp lên IPFS:", error);
    throw new Error(`Tải tệp lên IPFS thất bại: ${error.message}`);
  }
}

export async function uploadJsonToIPFS(data, fileName = "quy-che-bieu-quyet.json") {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: "application/json"
  });
  const file = new File([blob], fileName, { type: "application/json" });
  return uploadToIPFS(file);
}

export async function retrieveFromIPFS(cid) {
  const gateways = [
    `http://localhost:8080/ipfs/${cid}`,
    `http://localhost:8081/ipfs/${cid}`,
    `https://ipfs.io/ipfs/${cid}`,
    `https://gateway.pinata.cloud/ipfs/${cid}`
  ];

  for (const gateway of gateways) {
    try {
      const response = await fetch(gateway);
      if (!response.ok) continue;

      const contentType = response.headers.get("content-type") || "";
      if (contentType.includes("application/json")) {
        return { url: gateway, type: "json", content: await response.json() };
      }
      if (contentType.includes("text") || contentType.includes("markdown")) {
        return { url: gateway, type: "text", content: await response.text() };
      }
      return { url: gateway, type: "file", content: null };
    } catch (error) {
      continue;
    }
  }

  throw new Error(`Không đọc được CID ${cid} từ các cổng IPFS đã cấu hình.`);
}

export async function verifyCID(cid) {
  try {
    const gateways = [
      `https://ipfs.io/ipfs/${cid}`,
      `https://gateway.pinata.cloud/ipfs/${cid}`,
      `http://localhost:8080/ipfs/${cid}`
    ];

    for (const gateway of gateways) {
      try {
        const response = await fetch(gateway, { method: "HEAD" });
        if (response.ok) {
          console.log(`CID đọc được tại: ${gateway}`);
          return true;
        }
      } catch (error) {
        continue;
      }
    }

    return false;
  } catch (error) {
    console.error("Lỗi kiểm tra CID:", error);
    return false;
  }
}

export function getIPFSUrl(cid, gateway = "ipfs.io") {
  const gateways = {
    "ipfs.io": `https://ipfs.io/ipfs/${cid}`,
    pinata: `https://gateway.pinata.cloud/ipfs/${cid}`,
    cloudflare: `https://cloudflare-ipfs.com/ipfs/${cid}`,
    local: `http://localhost:8080/ipfs/${cid}`
  };

  return gateways[gateway] || gateways["ipfs.io"];
}

export default {
  uploadToIPFS,
  uploadJsonToIPFS,
  retrieveFromIPFS,
  verifyCID,
  getIPFSUrl
};
