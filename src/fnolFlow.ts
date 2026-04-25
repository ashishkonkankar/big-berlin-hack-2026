import { ClaimRecord, ClaimStage } from "./types.js";

const REQUIRED_FIELDS = [
  "fullName",
  "callbackNumber",
  "incidentDate",
  "incidentTime",
  "incidentLocation",
  "callerNarrative",
  "injuriesReported",
  "drivableStatus"
] as const;

const toIso = (): string => new Date().toISOString();

const extractPhone = (text: string): string | undefined => {
  const digits = text.replace(/\D/g, "");
  if (digits.length < 7) return undefined;
  return digits.length > 15 ? digits.slice(0, 15) : digits;
};

const yesNo = (text: string): string | undefined => {
  const t = text.toLowerCase();
  if (/(^|\s)(yes|yeah|yep|injured|true)(\s|$)/.test(t)) return "yes";
  if (/(^|\s)(no|nah|none|false)(\s|$)/.test(t)) return "no";
  return undefined;
};

const nextStage = (stage: ClaimStage): ClaimStage => {
  switch (stage) {
    case "safety_check":
      return "identity";
    case "identity":
      return "incident_basics";
    case "incident_basics":
      return "event_summary";
    case "event_summary":
      return "status_questions";
    case "status_questions":
      return "photo_offer";
    case "photo_offer":
      return "recap";
    case "recap":
      return "closed";
    default:
      return "closed";
  }
};

export const updateClaimFromCallerUtterance = (claim: ClaimRecord, utterance: string): ClaimRecord => {
  const text = utterance.trim();
  const lower = text.toLowerCase();

  if (claim.stage === "identity") {
    if (!claim.fields.fullName && text.length > 2) claim.fields.fullName = text.slice(0, 80);
    if (!claim.fields.callbackNumber) {
      const maybePhone = extractPhone(text);
      if (maybePhone) claim.fields.callbackNumber = maybePhone;
    }
    if (!claim.fields.policyNumber) {
      const maybePolicy = text.match(/\b[a-zA-Z0-9-]{6,20}\b/g)?.find((x) => /[0-9]/.test(x));
      if (maybePolicy) claim.fields.policyNumber = maybePolicy;
    }
  }

  if (claim.stage === "incident_basics") {
    if (!claim.fields.incidentDate) {
      const dateMatch = text.match(
        /\b(\d{1,2}[\/.-]\d{1,2}[\/.-]\d{2,4}|today|yesterday|last night)\b/i
      );
      if (dateMatch) claim.fields.incidentDate = dateMatch[1];
    }
    if (!claim.fields.incidentTime) {
      const timeMatch = text.match(/\b(\d{1,2}:\d{2}\s?(am|pm)?|\d{1,2}\s?(am|pm))\b/i);
      if (timeMatch) claim.fields.incidentTime = timeMatch[1];
    }
    if (!claim.fields.incidentLocation && text.length > 4) {
      claim.fields.incidentLocation = text.slice(0, 120);
    }
  }

  if (claim.stage === "event_summary") {
    if (!claim.fields.callerNarrative) claim.fields.callerNarrative = text.slice(0, 500);
    if (!claim.fields.numberOfVehicles) {
      const vehicles = text.match(/\b([1-9])\b/);
      if (vehicles) claim.fields.numberOfVehicles = vehicles[1];
    }
  }

  if (claim.stage === "status_questions") {
    if (!claim.fields.injuriesReported) {
      const injuries = yesNo(lower);
      if (injuries) claim.fields.injuriesReported = injuries;
    }
    if (!claim.fields.policePresent) {
      const police = yesNo(lower);
      if (police) claim.fields.policePresent = police;
    }
    if (!claim.fields.drivableStatus) {
      if (/\b(drivable|can drive|still drives)\b/i.test(lower)) claim.fields.drivableStatus = "yes";
      else if (/\b(not drivable|won't move|can't drive|towing)\b/i.test(lower))
        claim.fields.drivableStatus = "no";
    }
  }

  if (claim.stage === "photo_offer") {
    const answer = yesNo(lower);
    if (answer === "yes") claim.fields.photosRequested = true;
    if (answer === "no") claim.fields.photosRequested = false;
  }

  claim.updatedAt = toIso();
  claim.missingFields = REQUIRED_FIELDS.filter((key) => {
    const value = claim.fields[key];
    return value === undefined || value === "";
  }).map((x) => String(x));
  return claim;
};

export const getPromptForStage = (claim: ClaimRecord): string => {
  switch (claim.stage) {
    case "safety_check":
      return "Hello, claims support. First, is everyone safe and are you in a place where you can talk for a minute?";
    case "identity":
      return "Thank you. Can I take your full name and the best callback number in case we get disconnected?";
    case "incident_basics":
      return "Got it. When and where did the accident happen?";
    case "event_summary":
      return "Please briefly describe what happened and how many vehicles were involved.";
    case "status_questions":
      return "Were there any injuries, did police attend, and is your vehicle drivable right now?";
    case "photo_offer":
      return "If it is safe, I can text you a secure link now so you can upload a few photos. Would you like me to send that?";
    case "recap":
      return `Thank you. I have your claim with callback ${
        claim.fields.callbackNumber ?? "not confirmed"
      }, incident location ${claim.fields.incidentLocation ?? "not confirmed"}, injuries ${
        claim.fields.injuriesReported ?? "not confirmed"
      }, and drivable status ${claim.fields.drivableStatus ?? "not confirmed"}. Is that correct?`;
    case "closed":
    default:
      return "Thanks, your claim intake is saved. We will follow up shortly.";
  }
};

export const advanceStage = (claim: ClaimRecord): ClaimRecord => {
  claim.stage = nextStage(claim.stage);
  claim.updatedAt = toIso();
  return claim;
};
