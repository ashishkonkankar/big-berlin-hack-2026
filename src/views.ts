import { ClaimRecord } from "./types.js";

const esc = (value: string | undefined): string =>
  (value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");

export const uploadPageHtml = (claim: ClaimRecord): string => `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>INCA Claim Upload</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; max-width: 720px; }
    h1 { margin-bottom: 8px; }
    p { line-height: 1.4; }
    form { margin-top: 20px; display: grid; gap: 10px; }
    input, button { font-size: 16px; padding: 10px; }
  </style>
</head>
<body>
  <h1>INCA Claim Evidence Upload</h1>
  <p>Claim ID: <strong>${esc(claim.claimId)}</strong></p>
  <p>Please upload photos only when safe. A claims handler will review these with your call details.</p>
  <form method="post" enctype="multipart/form-data">
    <input name="photo" type="file" accept="image/*" required />
    <button type="submit">Upload photo</button>
  </form>
</body>
</html>`;

export const uploadSuccessHtml = (claimId: string): string => `<!doctype html>
<html>
<head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>Uploaded</title></head>
<body style="font-family: Arial, sans-serif; margin: 24px;">
  <h2>Upload received</h2>
  <p>Your photo has been attached to claim <strong>${esc(claimId)}</strong>.</p>
</body>
</html>`;

export const dashboardHtml = (claims: ClaimRecord[]): string => {
  const rows = claims
    .map((claim) => {
      const summary = esc(claim.fields.callerNarrative ?? "Pending");
      const missing = esc(claim.missingFields.join(", ") || "None");
      const images = claim.fields.photosReceived;
      return `<tr>
        <td>${esc(claim.claimId)}</td>
        <td>${esc(claim.fields.fullName ?? "Unknown")}</td>
        <td>${esc(claim.fields.callbackNumber ?? "Unknown")}</td>
        <td>${esc(claim.stage)}</td>
        <td>${images}</td>
        <td>${summary}</td>
        <td>${missing}</td>
      </tr>`;
    })
    .join("");

  return `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>INCA FNOL Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    table { width: 100%; border-collapse: collapse; }
    td, th { border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }
    th { background: #f5f5f5; }
  </style>
</head>
<body>
  <h1>INCA FNOL Intake Dashboard</h1>
  <p>Total claims: ${claims.length}</p>
  <table>
    <thead>
      <tr>
        <th>Claim ID</th>
        <th>Name</th>
        <th>Callback</th>
        <th>Stage</th>
        <th>Photos</th>
        <th>Narrative</th>
        <th>Missing</th>
      </tr>
    </thead>
    <tbody>${rows}</tbody>
  </table>
</body>
</html>`;
};
