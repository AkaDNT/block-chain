import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3002;
const DATA_DIR = path.join(__dirname, "data");
const DB_FILE = path.join(DATA_DIR, "saas-db.json");

app.use(cors());
app.use(express.json({ limit: "5mb" }));

const defaultDb = {
  organizations: [
    {
      id: "org-demo",
      name: "Quỹ cộng đồng mẫu",
      owner: "Ban điều hành",
      email: "hello@example.com",
      industry: "Doanh nghiệp nhỏ",
      description: "Tổ chức mẫu để demo FundFlow DAO."
    }
  ],
  recipients: [
    {
      id: "recipient-demo",
      name: "Đội vận hành",
      wallet: "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
      type: "Nhà cung cấp",
      note: "Ví nhận tiền demo",
      status: "Đang hoạt động"
    }
  ],
  budgets: [
    {
      id: "budget-demo",
      name: "Mua thiết bị văn phòng",
      limitEth: "1",
      owner: "Ban tài chính",
      status: "Mở",
      description: "Hạng mục mẫu để tạo đề xuất nhanh."
    }
  ],
  members: [
    {
      id: "member-demo",
      name: "Nguyễn Minh",
      email: "minh@example.com",
      wallet: "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
      role: "Quản trị",
      status: "Đang hoạt động"
    }
  ],
  documents: [
    {
      id: "document-demo",
      name: "Quy chế biểu quyết mẫu",
      type: "Quy chế",
      owner: "Ban điều hành",
      cid: ""
    }
  ],
  auditLogs: [],
  users: [
    { id: "user-admin", name: "Quản trị viên", email: "admin@fundflow.local", role: "Quản trị", password: "demo123" },
    { id: "user-finance", name: "Kế toán", email: "finance@fundflow.local", role: "Kế toán", password: "demo123" },
    { id: "user-member", name: "Thành viên", email: "member@fundflow.local", role: "Thành viên", password: "demo123" }
  ]
};

const resources = ["organizations", "recipients", "budgets", "members", "documents", "auditLogs", "users"];

function ensureDb() {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(DB_FILE)) fs.writeFileSync(DB_FILE, JSON.stringify(defaultDb, null, 2));
}

function readDb() {
  ensureDb();
  return JSON.parse(fs.readFileSync(DB_FILE, "utf8"));
}

function writeDb(db) {
  fs.writeFileSync(DB_FILE, JSON.stringify(db, null, 2));
}

function addAudit(db, action, resource, id) {
  db.auditLogs = [
    { id: `audit-${Date.now()}`, action, resource, recordId: id, time: new Date().toISOString() },
    ...(db.auditLogs || [])
  ].slice(0, 200);
}

function publicRecord(resource, record) {
  if (resource !== "users") return record;
  const { password, ...safeUser } = record;
  return safeUser;
}

app.get("/health", (req, res) => {
  res.json({ status: "ok", app: "FundFlow DAO SaaS API", storage: DB_FILE });
});

app.post("/api/auth/login", (req, res) => {
  const { email, password } = req.body;
  const db = readDb();
  const user = (db.users || []).find((item) => item.email === email && item.password === password);
  if (!user) return res.status(401).json({ error: "Email hoặc mật khẩu không đúng." });
  const safeUser = publicRecord("users", user);
  res.json({
    user: safeUser,
    token: `demo-token-${safeUser.id}`,
    permissions: {
      canManageSettings: safeUser.role === "Quản trị",
      canManageFinance: ["Quản trị", "Kế toán"].includes(safeUser.role),
      canVote: ["Quản trị", "Kế toán", "Thành viên"].includes(safeUser.role)
    }
  });
});

app.get("/api/saas/summary", (req, res) => {
  const db = readDb();
  res.json({
    organizations: db.organizations.length,
    recipients: db.recipients.length,
    budgets: db.budgets.length,
    members: db.members.length,
    documents: db.documents.length,
    auditLogs: db.auditLogs.length
  });
});

app.post("/api/saas/reset", (req, res) => {
  writeDb(defaultDb);
  res.json({ ok: true });
});

app.get("/api/saas/:resource", (req, res) => {
  const { resource } = req.params;
  if (!resources.includes(resource)) return res.status(404).json({ error: "Nhóm dữ liệu không tồn tại." });
  const db = readDb();
  res.json((db[resource] || []).map((record) => publicRecord(resource, record)));
});

app.get("/api/saas/:resource/:id", (req, res) => {
  const { resource, id } = req.params;
  if (!resources.includes(resource)) return res.status(404).json({ error: "Nhóm dữ liệu không tồn tại." });
  const db = readDb();
  const record = (db[resource] || []).find((item) => item.id === id);
  if (!record) return res.status(404).json({ error: "Không tìm thấy bản ghi." });
  res.json(publicRecord(resource, record));
});

app.post("/api/saas/:resource", (req, res) => {
  const { resource } = req.params;
  if (!resources.includes(resource) || ["auditLogs"].includes(resource)) return res.status(400).json({ error: "Không thể tạo bản ghi cho nhóm này." });
  const db = readDb();
  const record = {
    id: req.body.id || `${resource}-${Date.now()}`,
    ...req.body,
    createdAt: req.body.createdAt || new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  db[resource] = [record, ...(db[resource] || [])];
  addAudit(db, "Tạo mới", resource, record.id);
  writeDb(db);
  res.status(201).json(publicRecord(resource, record));
});

app.put("/api/saas/:resource/:id", (req, res) => {
  const { resource, id } = req.params;
  if (!resources.includes(resource) || ["auditLogs"].includes(resource)) return res.status(400).json({ error: "Không thể cập nhật nhóm này." });
  const db = readDb();
  const records = db[resource] || [];
  const index = records.findIndex((item) => item.id === id);
  if (index === -1) return res.status(404).json({ error: "Không tìm thấy bản ghi." });
  records[index] = { ...records[index], ...req.body, id, updatedAt: new Date().toISOString() };
  addAudit(db, "Cập nhật", resource, id);
  writeDb(db);
  res.json(publicRecord(resource, records[index]));
});

app.delete("/api/saas/:resource/:id", (req, res) => {
  const { resource, id } = req.params;
  if (!resources.includes(resource) || ["auditLogs"].includes(resource)) return res.status(400).json({ error: "Không thể xóa nhóm này." });
  const db = readDb();
  const before = (db[resource] || []).length;
  db[resource] = (db[resource] || []).filter((item) => item.id !== id);
  if (db[resource].length === before) return res.status(404).json({ error: "Không tìm thấy bản ghi." });
  addAudit(db, "Xóa", resource, id);
  writeDb(db);
  res.status(204).send();
});

app.listen(PORT, () => {
  ensureDb();
  console.log(`FundFlow DAO SaaS API đang chạy tại http://localhost:${PORT}`);
});
