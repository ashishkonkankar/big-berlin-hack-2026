import fs from "node:fs";
import path from "node:path";
import { ClaimRecord, ClaimStoreData } from "./types.js";

const DATA_DIR = path.resolve(process.cwd(), "data");
const DATA_FILE = path.join(DATA_DIR, "claims.json");

const emptyStore = (): ClaimStoreData => ({
  claims: {},
  callToClaim: {},
  uploadTokenToClaim: {}
});

export const ensureStore = (): void => {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  if (!fs.existsSync(DATA_FILE)) {
    fs.writeFileSync(DATA_FILE, JSON.stringify(emptyStore(), null, 2), "utf-8");
  }
};

export const readStore = (): ClaimStoreData => {
  ensureStore();
  const raw = fs.readFileSync(DATA_FILE, "utf-8");
  return JSON.parse(raw) as ClaimStoreData;
};

export const writeStore = (data: ClaimStoreData): void => {
  ensureStore();
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), "utf-8");
};

export const upsertClaim = (claim: ClaimRecord): void => {
  const db = readStore();
  db.claims[claim.claimId] = claim;
  db.callToClaim[claim.callId] = claim.claimId;
  if (claim.uploadToken) db.uploadTokenToClaim[claim.uploadToken] = claim.claimId;
  writeStore(db);
};

export const getClaimByCallId = (callId: string): ClaimRecord | null => {
  const db = readStore();
  const claimId = db.callToClaim[callId];
  if (!claimId) return null;
  return db.claims[claimId] ?? null;
};

export const getClaimByUploadToken = (token: string): ClaimRecord | null => {
  const db = readStore();
  const claimId = db.uploadTokenToClaim[token];
  if (!claimId) return null;
  return db.claims[claimId] ?? null;
};

export const getAllClaims = (): ClaimRecord[] => {
  const db = readStore();
  return Object.values(db.claims).sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
};
