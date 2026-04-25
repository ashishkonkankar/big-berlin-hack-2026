export type ClaimStage =
  | "safety_check"
  | "identity"
  | "incident_basics"
  | "event_summary"
  | "status_questions"
  | "photo_offer"
  | "recap"
  | "closed";

export interface FnolFields {
  fullName?: string;
  callbackNumber?: string;
  policyNumber?: string;
  incidentDate?: string;
  incidentTime?: string;
  incidentLocation?: string;
  cityOrRegion?: string;
  callerNarrative?: string;
  damageDescription?: string;
  otherParty?: string;
  numberOfVehicles?: string;
  injuriesReported?: string;
  policePresent?: string;
  policeReport?: string;
  drivableStatus?: string;
  vehicleDescription?: string;
  coverageType?: string;
  currentAgentState?: string;
  photosRequested?: boolean;
  photosReceived: number;
}

export interface ClaimRecord {
  claimId: string;
  callId: string;
  sourceChannel: "phone";
  stage: ClaimStage;
  fields: FnolFields;
  transcript: Array<{ role: "agent" | "caller"; text: string; ts: string }>;
  missingFields: string[];
  createdAt: string;
  updatedAt: string;
  uploadToken?: string;
  uploadLinkSentAt?: string;
  imageFindings: string[];
}

export interface ClaimStoreData {
  claims: Record<string, ClaimRecord>;
  callToClaim: Record<string, string>;
  uploadTokenToClaim: Record<string, string>;
}
