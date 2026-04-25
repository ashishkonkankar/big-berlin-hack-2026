# DeepMind Master Brief: Human-Passing Insurance Voice Agent for INCA x Gradium

## How to use this document

This document is designed as a master context file for Google DeepMind or Gemini. It consolidates the hackathon brief, product strategy, architecture, API key checklist, data requirements, recommended stack, documentation plan, and a paste-ready master prompt so the model can help produce specs, technical docs, product docs, investor-style summaries, implementation plans, and partner access requests. The project context combines INCA's claims-intake positioning with Gradium's realtime voice infrastructure and the hackathon requirement to convince jurors they are speaking to a human. [web:47][page:1][web:104]

Important assumption: the phrase "UPI keys" is interpreted here as **API keys**. If "UPI" was meant literally as Unified Payments Interface, that is unrelated to the current insurance voice-agent challenge and should be ignored unless payment collection is introduced later. The partner materials and project needs point to API keys, credits, temporary model access, and telecom credentials instead. [page:1][page:2][web:90]

## Project objective

Build a phone-based voice agent for first notice of loss (FNOL) that handles an inbound accident claim call, sounds human enough that more than 50% of jurors vote "human," and produces complete, high-quality claim documentation. The system must remain usable across dialects, interruptions, and noisy roadside conditions, which means the design cannot rely on a clean happy-path audio environment. [web:68][web:71][web:74][web:76]

The strongest version of the concept is a **roadside claims intake agent** that can do four things well:
- answer an inbound phone call naturally,
- collect core FNOL facts in a calm, human-sounding way,
- send an SMS with a secure upload link for photos,
- analyze those images and combine them with the call transcript into a structured claim record. [web:104][web:108][web:109][web:110][web:112]

This is stronger than a pure voice bot because it looks like a real insurance workflow. Modern FNOL flows increasingly combine conversational intake, guided digital forms, evidence upload, and downstream automation in one claim session. [web:104][web:105][web:111][web:116]

## Challenge summary

The hackathon is not judged only by external observers. The callers themselves are the judges, and they will cast a blind vote at the end of the call: human or AI. That means success depends heavily on conversation feel, interruption handling, pacing, recovery after mishearing, and the ability to act like a competent claims handler rather than a generic assistant. [web:67][web:70][web:76]

The solution also needs complete documentation quality. In FNOL, a useful intake generally includes policyholder or claimant identity, callback contact, incident date and time, location, what happened, involved parties, vehicle details, injuries, drivable status, police involvement, and available evidence. The workflow should collect these essentials reliably rather than attempting broad open-domain conversation. [web:68][web:71][web:74]

## Product thesis

The winning product thesis is:

> Create a human-passing inbound claims intake agent that speaks naturally during a stressful roadside incident, requests photo evidence at the right moment by SMS, analyzes the uploaded images, and creates a complete FNOL package for an insurer.

This product thesis aligns with INCA's public positioning around AI-native end-to-end claims handling and fast claims resolution. It also aligns with Gradium's public positioning around low-latency streaming speech-to-text, text-to-speech, realtime interactions, custom pronunciation, multilingual speech, and function-calling support for interactive agents. [web:45][web:47][page:1][web:80]

## Recommended system behavior

The agent should sound like an experienced claims intake specialist, not an AI assistant. It should be calm, concise, lightly empathetic, and operational. The opening should acknowledge stress but move quickly into safety and fact collection. The goal is not theatrical friendliness; the goal is confident competence. [web:72][web:76]

Recommended call style:
- Short turns, usually one question at a time.
- Natural acknowledgments such as “Okay,” “Got it,” “One second,” and “Let me confirm that.”
- Immediate barge-in support so the system stops speaking when the caller talks. [web:67][web:70]
- Recovery behavior after uncertainty: repeat or narrow the question instead of pretending the answer was heard correctly. [web:67][web:74]
- Explicit safety-first language before asking for photos. Public insurer guidance recommends collecting photos only when it is safe to do so. [web:110][web:113]

## Core user journey

### Primary journey

1. Caller dials the claims number.
2. Agent answers and verifies whether everyone is safe.
3. Agent collects identity and callback details.
4. Agent collects accident basics: when, where, vehicles involved, what happened.
5. Agent asks status questions: injuries, drivable or not, police involved, third-party details.
6. Agent offers to send an SMS upload link for photos if it is safe.
7. Caller receives the text, opens a secure link, and uploads images.
8. Multimodal analysis reviews the images and produces a structured visual summary.
9. The claim record updates with transcript, extracted fields, image findings, and missing items.
10. Agent closes the call with next steps and a recap. [web:104][web:108][web:109][web:110][web:112]

### Why this journey is strong

This flow gives the juror a believable experience of speaking with a competent claims professional while also producing a richer output than voice alone. It creates a visible product advantage: the voice agent does not merely talk, it advances the claim by coordinating evidence capture and documentation. [web:104][web:105][web:109]

## Required information to capture

### Mandatory FNOL data model

The system should capture the following structured fields during or immediately after the call:

| Category | Fields |
|---|---|
| Claim identity | claim_id, call_id, timestamp_created, source_channel |
| Caller identity | full_name, callback_number, email_if_available, role_of_caller |
| Policy context | policy_number_if_known, vehicle_registration_if_known, insured_name_if_different |
| Incident basics | incident_date, incident_time, incident_location, road_or_highway_name, city_or_region |
| Event summary | caller_narrative, impact_type, road_conditions_if_mentioned, weather_if_mentioned |
| Vehicle details | claimant_vehicle_make_model_if_known, third_party_vehicle_if_known, drivable_status |
| Human safety | injuries_reported, emergency_services_contacted, safe_to_continue_call |
| Third parties | number_of_other_vehicles, third_party_name_if_known, plate_if_known, witnesses_if_any |
| Official involvement | police_present, police_report_reference_if_available |
| Damage and evidence | visible_damage_areas, photos_requested, photos_received, image_analysis_summary |
| Next steps | towing_needed, follow_up_required, missing_fields, claim_routing_recommendation |
| Quality metadata | transcript_confidence, image_confidence, fields_confirmed_with_caller |

These fields are a practical interpretation of typical FNOL requirements described by insurance sources and claims-intake guidance. The goal is to open a usable claim, not to determine final liability on the call. [web:68][web:71][web:74][web:111]

### Critical confirmations

The agent should explicitly confirm the highest-risk fields before call end:
- callback number,
- accident location,
- date and time,
- whether anyone is injured,
- whether the vehicle is drivable,
- whether photo evidence was successfully requested or received. [web:71][web:74][web:110]

## Photo capture strategy

### Why photo upload matters

SMS-based photo upload makes the experience more realistic and materially improves claim quality. Public guidance from insurers shows that customers are often asked to capture overall damage, close-ups, the wider scene, vehicle identifiers, and other supporting context through mobile-friendly flows. [web:110][web:113]

### What the SMS should do

The system should send a text message containing:
- a secure one-time upload link,
- a short safety warning,
- simple photo instructions,
- reassurance that the claim will continue even if not all photos are available immediately. [web:104][web:109][web:110]

### Recommended photo prompts

Ask for only 3 to 5 safe, high-value images:
- one wide image of the vehicle damage,
- one close-up of the main damaged area,
- one wide image of the scene,
- one image of the other vehicle if safe,
- plate or VIN only if visible and safe. [web:110][web:113]

### What image analysis should do

The image model should not attempt to finalize liability. It should:
- describe what is visible,
- identify obvious damage zones,
- count visible vehicles if possible,
- extract readable identifying text when reliable,
- compare image evidence to the caller's description,
- flag inconsistencies or missing evidence for review. [web:108][web:112]

## Recommended technology architecture

### High-level stack

| Layer | Recommended role | Strong options |
|---|---|---|
| Telephony | Inbound calling, phone number, call routing, media stream, SMS | Twilio, Telnyx, Vonage |
| Voice runtime | Realtime STT and TTS, human-like voice, barge-in, pronunciation control | Gradium [page:1] |
| Reasoning / orchestration | Dialogue policy, slot filling, summarization, function calling, multimodal reasoning | Google DeepMind / Gemini [web:90][web:91][web:93] |
| Retrieval | Real-time search, extraction, crawling for edge cases or enrichment | Tavily [page:2][web:94] |
| Backend | Session orchestration, APIs, webhooks, storage, security | Node.js/TypeScript or Python/FastAPI |
| Image upload UI | Mobile-friendly upload page opened from SMS | Next.js, React, or a simple hosted form |
| Storage | Claim records, transcripts, image metadata | Supabase/Postgres, Firebase, or plain Postgres |
| Blob storage | Uploaded photos, signed URLs | S3, Cloudflare R2, GCS |
| Dashboard | Claim review UI, transcript + fields + image findings | React, Lovable-generated UI if helpful |

### Recommended event flow

1. Inbound phone number receives the call.
2. Telephony provider streams audio to the voice service.
3. Gradium performs realtime speech-to-text and realtime text-to-speech. [page:1]
4. The orchestration layer maintains dialogue state, listens for interruption, and calls Gemini for next-step reasoning.
5. The agent fills structured FNOL slots continuously.
6. When the agent decides photos are needed, the backend triggers SMS.
7. The caller opens the upload link, and images are stored under the claim session.
8. Gemini or another multimodal model analyzes the images and returns structured findings.
9. The backend merges voice and image outputs into the claim record.
10. The dashboard presents final documentation, confidence levels, and missing fields. [page:1][web:104][web:109][web:112]

### Why this architecture is strong

This setup clearly separates the parts that must feel human in realtime from the parts that can be slightly asynchronous. Voice quality and interruption belong in the low-latency Gradium loop, while heavier reasoning, multimodal analysis, and documentation generation can sit behind it in Gemini and the backend. [page:1][web:80]

## API keys, credentials, and access needed

This section answers the main operational question: **what API keys and credentials are needed to build this?**

### Absolutely required

| Service | Why needed | What credential or access is required |
|---|---|---|
| Gradium | Realtime STT, TTS, voice interaction, pronunciation, agent behavior | Gradium account, project/org approval, API key, model access, credit allocation [page:1] |
| Google DeepMind / Gemini | Dialogue reasoning, summarization, multimodal image analysis, structured extraction | Temporary hackathon account or API key, model access, quota information [web:90][web:91] |
| Telephony provider | Inbound calls, phone number, call webhook, media streaming, SMS | Account SID / API key, auth token, phone number, SMS enablement, webhook URL |
| Backend host | Public endpoints for telephony callbacks, SMS upload URLs, dashboard | Deploy target and environment secrets |
| Blob storage | Store uploaded accident photos securely | Bucket credentials or signed URL capability |
| Database | Store claim sessions, transcripts, metadata, extracted fields | Connection string or hosted DB credentials |

### Very useful but optional

| Service | Why useful | What is needed |
|---|---|---|
| Tavily | Real-time retrieval, enrichment, lookup, extraction | API key and credit balance [page:2][web:94] |
| Lovable | Fast internal dashboard or claim UI generation | Account plus hackathon redemption code |
| Entire | Developer workflow and agent-human collaboration tooling | CLI install and account access [web:95][web:101] |
| Error monitoring | Faster debugging during hackathon | Sentry or equivalent DSN |
| Analytics / observability | Latency tracking, failure analysis | Logging sink or APM key |

### Practical key checklist

Request or confirm the following before implementation starts:
- Gradium API key.
- Gradium credits allocation.
- Confirmation of accessible STT/TTS models and any realtime websocket endpoint details. [page:1]
- Access to a Google DeepMind / Gemini temporary account or API key. [web:90][web:91]
- Telephony provider account with a phone number that supports inbound calling.
- SMS-enabled number or messaging credentials.
- Public webhook URL or deployment environment.
- Storage bucket credentials or pre-signed upload capability.
- Database credentials.
- Tavily API key if retrieval or research enrichment is included. [page:2]

## Information to request from organizers, partners, and stakeholders

### From INCA

Ask for:
- the short brief on how real claims intake calls sound,
- examples of common opening lines,
- must-have fields for opening a car accident claim,
- examples of how agents handle distressed callers,
- whether police report or towing information is considered essential in their intake logic,
- phone number provisioning support,
- any constraints on what should never be promised during the call. [web:47][web:75]

### From Gradium

Ask for:
- account activation under the correct organization,
- recommended low-latency STT and TTS models for realtime telephony,
- websocket or streaming examples,
- guidance on barge-in handling,
- pronunciation dictionary support for addresses, plates, policy numbers, and names,
- multilingual or accent-handling best practices,
- rate limits, concurrency, and latency expectations. [page:1][web:80]

### From Google DeepMind / Gemini

Ask for:
- which Gemini model is best for multimodal claims analysis,
- streaming versus non-streaming options,
- function calling support,
- image upload size limits,
- JSON schema or structured output best practices,
- quota limits under the temporary account,
- latency expectations for live and post-call tasks. [web:90][web:91][web:93]

### From telephony provider

Ask for:
- inbound number provisioning,
- media stream setup,
- real-time audio webhook or websocket documentation,
- SMS delivery support in the event country,
- call recording policy,
- number verification needs,
- test environment details. [web:109]

## Human-pass design rules

The system should optimize for caller perception. The main rules are:
- Do not speak in long paragraphs.
- Prefer short acknowledgments and one question at a time.
- Stop speaking immediately when the user interrupts. [web:67][web:70]
- Confirm critical entities instead of guessing when audio is noisy. [web:74][web:76]
- Avoid generic assistant language such as “I can help you with that today.”
- Use slightly imperfect but controlled conversational phrasing rather than over-polished robotic speech.
- Maintain a steady professional tone rather than exaggerated warmth.

The juror should feel that the agent is a practiced claims handler who knows what to ask next. That impression is more important than sounding “magically AI-powered.” [web:72][web:76]

## Example call structure

### Suggested opening

“Hello, claims support. First, is everyone safe and are you in a place where you can talk for a minute?”

This works because it feels operational, caring, and specific to roadside claims. It gets immediately into the highest-priority branch: safety. [web:71][web:74]

### High-quality intake sequence

1. Safety and ability to continue.
2. Name and callback number.
3. Policy number if available, otherwise skip.
4. When and where the accident happened.
5. Brief description of what happened.
6. Number of vehicles involved.
7. Injuries, police, drivable status.
8. Offer SMS photo upload if safe.
9. Read back key facts.
10. Explain next steps.

### Closing line

“Thank you. I’ve opened the claim, I’ve got your callback number as [X], and I’ve sent the upload link by text. If anything changes, use that link or call back on this number.”

## Documentation outputs to generate

The system should be able to generate the following documents automatically:
- claim intake summary,
- structured FNOL JSON,
- transcript with timestamps,
- image analysis summary,
- missing-information checklist,
- claims handler review note,
- hackathon submission write-up,
- sponsor-usage explanation for Gradium,
- architecture note,
- product one-pager,
- demo script. [web:104][page:1]

## Best use of partner technologies

### Gradium

Gradium should be presented as the core realtime conversational engine. Public documentation highlights low-latency streaming TTS, STT, multilingual support, pronunciation dictionaries, function calling support, and expected sub-300ms time to first token for streaming. Those strengths map directly to interruption handling, natural voice timing, and correct read-back of structured insurance data. [page:1][web:80]

### Google DeepMind / Gemini

Gemini is best used for dialogue reasoning, extraction, summarization, and multimodal interpretation of uploaded accident photos. Public hackathon references around Gemini emphasize multimodal reasoning and frontier model capability rather than telephony infrastructure, so Gemini should be positioned as the intelligence and documentation layer rather than the core voice transport layer. [web:90][web:91][web:93]

### Tavily

Tavily is useful when the system needs live retrieval or external enrichment, such as pulling relevant support information, extracting context from a web resource, or validating live details. It is not required for the core call loop, but it can meaningfully enrich post-call workflows and edge-case handling. [page:2][web:94]

## Implementation plan for a small team

### Phase 1: Working call loop

Goal: answer a phone call, capture audio, transcribe, generate short responses, and speak them back naturally. This is the hardest perception layer and should be solved first. [page:1][web:76]

### Phase 2: Dialogue state machine

Goal: move from generic chatting to a deterministic FNOL flow. Add states for safety, identity, incident basics, damage, injuries, third parties, photo request, recap, and close.

### Phase 3: SMS upload flow

Goal: send a secure upload link during the call and store photos under the active session. Keep the upload experience extremely simple on mobile. [web:104][web:110]

### Phase 4: Image understanding

Goal: run image analysis after upload and attach structured findings to the claim record. Start with description, damage area, visible vehicles, readable text, and mismatch flags. [web:108][web:112]

### Phase 5: Dashboard and final docs

Goal: present one polished review screen that shows the transcript, extracted fields, uploaded images, image summary, and missing items. This is what makes the product look operationally credible.

## Recommended technical integrations

### Simplest reliable build

- Twilio or Telnyx for inbound call and SMS.
- Gradium for realtime STT/TTS. [page:1]
- Node.js or Python backend for orchestration.
- Gemini for reasoning and image analysis. [web:90][web:91]
- Supabase or Postgres for claim storage.
- S3 or Cloudflare R2 for photo uploads.
- Basic React or Lovable-generated internal dashboard.

### Slightly more advanced build

- Add Tavily for enrichment or web research workflows. [page:2]
- Add confidence scoring for critical entities.
- Add pronunciation dictionary for structured read-backs through Gradium. [page:1][web:80]
- Add automatic mismatch detection between transcript and photo analysis.

## Risks and mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| High latency | Jurors quickly perceive AI if pauses feel unnatural | Keep voice loop on Gradium, use short prompts, stream everything [page:1][web:76] |
| Weak interruption handling | Over-talking is a major AI tell | Implement immediate TTS stop on caller speech [web:67][web:70] |
| Noisy audio | Roadside conditions can damage accuracy | Confirm critical slots, use repair questions, do not guess [web:74][web:76] |
| Over-scoped build | Small teams lose time on broad systems | Focus on one exceptional accident intake flow |
| Unsafe photo instructions | Asking for evidence at the wrong time is harmful | Always gate photo requests behind safety check [web:110][web:113] |
| Incomplete docs | Good call but poor claim output weakens the product | Fill structured fields during the call, not only after it [web:68][web:71] |

## Submission framing

A strong submission description is:

“An inbound roadside claims agent that sounds like a trained claims handler, captures first-notice-of-loss information over the phone, sends a secure SMS evidence link when it is safe, analyzes uploaded accident photos, and produces a complete structured FNOL record. Gradium powers the realtime conversational layer, Gemini powers reasoning and multimodal claim understanding, and the platform combines voice and visual evidence into insurer-ready documentation.” [page:1][web:90][web:104][web:112]

## Master prompt for Google DeepMind / Gemini

Copy the prompt below into Gemini as the working project brief.

---

You are the lead technical architect, product strategist, and documentation writer for a hackathon project.

Your job is to help design, document, and scope a production-like prototype for an insurance voice agent challenge.

### Project context

The project is a phone-based AI voice agent for inbound insurance claims intake. A caller phones in after a roadside car accident. The goal is to convince more than 50% of callers that they are speaking to a human, while also collecting high-quality first-notice-of-loss (FNOL) information and producing complete internal documentation.

The system must work under noisy conditions, dialect variation, caller stress, and interruptions. The ideal demo also sends an SMS during the call with a secure upload link so the caller can upload accident photos from their phone. Those photos are then analyzed and merged with the call transcript into a structured claim record.

### Product goals

1. Sound human enough to pass blind caller voting.
2. Gather the essential facts needed to open a car accident claim.
3. Send a text message with a secure upload link for photos.
4. Analyze uploaded images and compare them to the spoken report.
5. Produce a clean, structured FNOL output and internal claims summary.
6. Be realistic enough to demo to insurers and hackathon judges.

### Key design principles

- The voice agent should sound like an experienced claims intake handler, not a generic chatbot.
- Responses should be short, natural, and interruptible.
- The system should prioritize safety before photo requests.
- The system should confirm critical facts instead of guessing under poor audio conditions.
- The architecture should clearly separate realtime voice tasks from slower reasoning and documentation tasks.

### Mandatory claim fields to capture

Capture these fields in structured form:
- claim_id
- call_id
- created_at
- caller_full_name
- callback_number
- caller_role
- policy_number_if_available
- vehicle_registration_if_available
- incident_date
- incident_time
- incident_location
- road_name_or_highway
- city_or_region
- caller_narrative
- impact_type
- number_of_vehicles
- injuries_reported
- emergency_services_contacted
- police_present
- police_reference_if_available
- claimant_vehicle_details_if_available
- third_party_details_if_available
- drivable_status
- towing_needed
- visible_damage_areas
- photos_requested
- photos_received
- image_analysis_summary
- missing_fields
- confidence_notes
- final_claim_summary

### Recommended technology assumptions

Use this as the default architecture unless a better option is proposed:
- Telephony provider for inbound number, call handling, audio streaming, and SMS.
- Gradium for realtime STT and TTS.
- Google Gemini for dialogue reasoning, summarization, and multimodal image analysis.
- Tavily optionally for real-time search or enrichment.
- Node.js/TypeScript or Python backend for orchestration.
- Postgres or Supabase for claim records.
- S3 / R2 / GCS-style blob storage for uploaded photos.
- A lightweight web dashboard for claims review.

### What is needed from you

Using all of the context above, produce the following in order:

1. A complete product requirements document for the prototype.
2. A technical architecture document with services, data flow, and event flow.
3. A list of all API keys, accounts, quotas, and credentials required.
4. A checklist of information to request from INCA, Gradium, Google DeepMind, and the telephony provider.
5. A proposed call script with fallback responses, interruption handling, and safety-first logic.
6. A JSON schema for the structured FNOL output.
7. A multimodal image analysis prompt for accident photos.
8. An SMS upload flow specification, including what text to send and what instructions to display on the upload page.
9. A claims dashboard specification showing what fields, statuses, and media should be visible.
10. A hackathon implementation plan split into 24-hour, 48-hour, and polish phases.
11. A risk register with likely failure modes and mitigations.
12. A final submission summary emphasizing best use of Gradium.

### Output format

- Be concrete and implementation-ready.
- Prefer tables where useful.
- Use concise but complete language.
- Include recommended defaults when information is missing.
- State assumptions clearly.
- When useful, provide example JSON, API payload shapes, and component structures.
- Prioritize realistic hackathon execution over enterprise complexity.

### Additional constraints

- Optimize for a 2-person design-led team with limited time.
- Favor one excellent car-accident FNOL journey over broad insurance coverage.
- Keep the voice interaction believable and low-latency.
- Keep photo upload mobile-friendly and extremely simple.
- Avoid overengineering unless it materially improves the demo.

Start by producing the full product requirements document and the API-key / credential checklist.

---

## Short partner access request templates

### Request for Gradium access

Hello Gradium team,

A hackathon project is being built for inbound insurance claim intake. Gradium is intended to power the realtime conversational layer, including streaming speech-to-text, text-to-speech, and natural turn-taking for a roadside accident FNOL experience.

Please enable the following if available:
- API key / project access
- recommended low-latency realtime STT model
- recommended low-latency TTS voice/model
- websocket or streaming examples
- pronunciation dictionary support for names, addresses, policy numbers, and license plates
- rate-limit and concurrency guidance

The intended use case is a human-sounding inbound insurance claims phone call with SMS evidence capture and structured documentation.

### Request for Google DeepMind / Gemini access

Hello team,

A hackathon project is being built for multimodal insurance claims intake. Gemini will be used for dialogue reasoning, structured extraction, and image analysis of accident photos uploaded during the claim process.

Please confirm:
- temporary account or API access
- recommended model for multimodal image understanding
- structured JSON output support
- function calling support
- quotas and limits
- best practices for low-latency use in a voice-adjacent workflow

### Request for telephony / SMS setup

Hello,

A hackathon prototype is being built for inbound insurance claims intake by phone. The project requires:
- a phone number for inbound calling,
- support for media streaming or audio webhook integration,
- SMS sending from the same or linked number,
- webhook configuration guidance,
- confirmation of supported regions for testing.

The use case is a caller reporting a roadside accident, with the system sending a secure photo-upload link during the call.

## Final recommendation

The best demo is not “AI that talks.” The best demo is a believable roadside claims worker in software: it speaks naturally, handles interruptions, asks the right FNOL questions, sends an evidence link at the right time, analyzes the uploaded photos, and leaves behind a claim file that looks immediately useful to an insurer. That is the product, the story, and the sponsor strategy in one. [web:47][page:1][web:104][web:112]

## New section: idea inventory

This section consolidates the strongest product ideas currently in scope for the hackathon concept.

### Idea 1: Human-passing inbound FNOL voice agent

A roadside claims voice agent that answers inbound calls, sounds like a trained claims handler, collects the information needed to open a claim, and performs well under accents, interruptions, and roadside noise. This remains the core concept because the challenge is judged by blind human-pass voting from callers. [web:68][web:71][web:76]

### Idea 2: Safety-first opening before claims questions

Before asking for claim details, the agent should quickly check whether the caller is safe, whether anyone is injured, and whether emergency help is already on the way. This matches good FNOL practice because the first notice of loss is often a stressful moment and public claims guidance emphasizes safety before documentation. [web:71][web:74][web:110][web:124]

A recommended opening sequence is:
- “First, is everyone safe?”
- “Are you in a safe place to talk right now?”
- “Does anyone need an ambulance or roadside help?”
- “If you need immediate help, I can connect support before we continue.”

### Idea 3: Assistance routing from the voice agent

If the caller is injured, stranded, distressed, or unable to continue, the system should be able to trigger the next best action instead of forcing the full claims flow immediately. Examples include ambulance escalation, towing or roadside recovery, concierge-style assistance, or a callback workflow. This fits the broader claims-intake idea that AI can surface urgent needs and recommend next actions at intake rather than only collecting form fields. [web:124][web:128][web:130]

The prototype does not need real emergency dispatch integration to tell this story. A hackathon version can simulate:
- roadside assistance request created,
- emergency escalation recommended,
- recovery partner contacted,
- concierge follow-up scheduled,
- live callback promised.

### Idea 4: SMS photo upload during the call

The agent should send a secure text message with a mobile upload link so the caller can provide accident photos safely from the roadside. Digital FNOL flows increasingly combine conversational intake with evidence capture, and insurers already guide customers to upload photos of vehicle damage and the scene. [web:104][web:105][web:110][web:113]

### Idea 5: Multimodal claim understanding

Once photos are uploaded, the system should analyze them and compare the visual evidence against the spoken narrative. A strong version would identify damage areas, visible vehicles, road context, readable identifiers where reliable, and mismatch signals between the caller story and the images. [web:108][web:112][web:125]

### Idea 6: Fraud and anomaly signals at FNOL

The system should evaluate fraud signals during intake rather than waiting until much later in the claim. Industry sources describe growing use of anomaly detection, image authenticity checks, metadata verification, and cross-claim correlation directly at FNOL, especially as generative AI makes altered or synthetic evidence more common. [web:119][web:122][web:125][web:131]

### Idea 7: Claims dashboard that feels operationally real

The internal claims screen should show transcript, extracted fields, uploaded images, visual analysis summary, missing items, urgency status, and fraud indicators. This makes the prototype feel like a real insurer workflow instead of a thin voice demo. [web:104][web:120][web:130]

## New section: safety-first triage and empathy layer

This is one of the strongest product ideas because it makes the agent feel more human and more useful.

### Product principle

The agent should act like a trained claims intake professional during a stressful moment. That means empathy is expressed through calm prioritization: safety first, then help, then documentation. Sources discussing FNOL and empathy in claims intake emphasize that urgent needs, reassurance, and supportive next-step guidance improve both experience and information quality. [web:124][web:121]

### Triage order

The first decision tree should be:
1. Is everyone safe?
2. Is the caller in a safe place to continue talking?
3. Are there injuries or distress?
4. Is emergency response or roadside assistance needed?
5. If safe, proceed into claim intake.

### Recommended triage states

| State | Trigger | System action |
|---|---|---|
| Safe to continue | No injuries, caller stable | Continue FNOL intake |
| Injured or medical concern | Caller mentions pain, injury, shock, faintness | Slow the pace, recommend emergency help, offer escalation |
| Unsafe roadside position | Highway shoulder, active traffic, poor visibility | Shorten questions, prioritize callback and assistance |
| Vehicle not drivable | Caller stranded | Offer towing/recovery flow or partner handoff |
| Caller distressed | Crying, panic, confusion | Use shorter empathetic phrasing, repeat less, recap more |

### Example empathetic language

- “I’m sorry this happened. First, I want to make sure you’re safe.”
- “We can handle the claim in a moment, but first tell me whether anyone is hurt.”
- “If the car isn’t drivable, I can help arrange the next step before we continue.”
- “Take your time. I’ll keep this simple.”

This style is better than generic assistant language because it sounds like a person trained for a stressful intake moment. [web:124]

## New section: fraud signals to detect during FNOL

A fraud layer should support the intake flow without making the agent accusatory. The system should silently flag risk indicators for internal review and route suspicious cases for deeper assessment. AI-driven FNOL references describe fraud detection at intake through narrative anomalies, suspicious metadata, image mismatch, and cross-claim patterning. [web:82][web:122][web:125]

### Voice and narrative signals

Potential call-time signals include:
- inconsistent timeline or location descriptions,
- changing number of vehicles or passengers,
- vague but rehearsed-sounding accident narratives,
- unusual reluctance to confirm basics,
- caller role confusion, such as uncertainty about relation to the insured,
- repeated corrections around high-value details.

### Image and evidence signals

Potential image-time signals include:
- mismatch between spoken impact description and visible damage,
- altered or AI-generated images,
- reused photos from previous claims,
- suspicious EXIF or upload metadata,
- edited license plates or scene details,
- invoices or documents that appear synthetic or inconsistent. [web:119][web:122][web:125][web:131]

### Operational fraud outputs

The prototype can surface:
- fraud risk score,
- suspicious narrative flag,
- image authenticity review flag,
- transcript/image mismatch flag,
- duplicate-claim review recommendation,
- mandatory human review routing.

### Important design constraint

The voice agent should never directly accuse the caller of fraud during the demo. The better product behavior is quiet scoring and smart routing in the background. [web:122][web:125]

## New section: comparable companies and startups

The exact combination of INCA's claims-handling focus and a human-passing voice-first FNOL agent is still relatively differentiated, but several adjacent companies and solution patterns are relevant.

### Corgi

Corgi is an AI-native full-stack insurance carrier for startups and publicly describes AI systems that support underwriting, claims, and policy operations. It is not specifically a roadside FNOL voice-intake company, but it is relevant as an example of an AI-native insurer building claims as part of a vertically integrated insurance stack. [web:123][web:126][web:129][web:132]

### Five Sigma / AI claims automation pattern

Industry overviews increasingly point to AI-native claims operations platforms that automate FNOL, triage, and routing, with products focused on reducing manual intake work and accelerating claims handling. References discussing AI claims automation highlight the pattern of using AI for severity scoring, fraud scoring, and faster claim movement from intake to decision. [web:120][web:128]

### Inaza / photo-to-decision pattern

Inaza is relevant because it emphasizes a path from photo upload toward fast claim decisioning. That makes it a useful reference for the multimodal evidence-capture part of the concept, especially when thinking about how a mobile upload flow can support downstream decisioning. [web:108]

### Datamatics / enterprise intake-agent pattern

Datamatics describes a claims intake agent that collects FNOL via voice or chat and validates data in real time. This is useful as a reference for the intake-agent workflow, even if the positioning is enterprise services rather than startup product. [web:130]

### Kagen / voice-AI-for-insurance pattern

Kagen frames AI voice agents as a way to guide structured questions, capture and validate data in real time, and push information directly into claims systems. That is close to the core workflow needed here, especially for the live call loop and structured documentation layer. [web:82]

### Nurix / fraud-and-FNOL pattern

Nurix is relevant as a reference for integrating fraud signals at FNOL through anomaly detection, image authenticity checks, and cross-claim correlation. This is especially useful for shaping the internal fraud-review layer of the prototype. [web:122]

### What looks most similar to INCA

The closest comparison is not a single startup but a combination of patterns:
- AI-native claims intake and automation,
- photo-driven evidence capture,
- real-time fraud detection,
- insurer workflow integration,
- and increasingly, voice-based FNOL.

INCA appears differentiated if the project combines all of these into one roadside claim experience with a convincing voice layer. Most comparable references emphasize one or two parts of the stack rather than the full inbound-call-to-photo-to-documentation loop. [web:47][web:82][web:108][web:122][web:130]

## New section: ideas to ask Gemini for next

Use Gemini to turn these sections into the next documents:
- a “safety-first triage PRD,”
- a “fraud signals and review logic” spec,
- a “competitor landscape” table comparing INCA, Corgi, photo-claims products, and AI intake agents,
- a revised system prompt for the voice agent with empathy and escalation built in,
- a claims dashboard spec showing risk, urgency, and service actions.


## New section: humanness brief and behavioral voice design

This section upgrades the brief with a more precise definition of what it means for the agent to sound human. The key principle is that humanness is not mainly a voice-quality problem; it is a behavioral design problem. The voice is only convincing when timing, acknowledgment, turn-taking, empathy, silence, and repair behavior all feel present and situationally appropriate.

### Core humanness thesis

The agent should behave like a calm, experienced claims professional during one of the worst moments of a caller's day. That means warm and unhurried pacing, short acknowledgments before questions, deliberate pauses before emotionally significant responses, one question at a time, and graceful handling of silence or repetition.

### Behavioral rules to encode

- Warm, steady, unhurried delivery; do not sound like a rushed contact-center script.
- Slightly slower-than-default speaking rate.
- Brief pause before empathy responses.
- Brief pause after questions to signal genuine listening.
- Every response after caller speech starts with a short acknowledgment.
- One question at a time, always.
- Silence is not failure; allow silence before reprompting.
- Empathy should be short, plain, and never theatrical.
- Controlled imperfection is allowed in longer responses, but not constant filler.
- Never assume the caller is uninjured or “fine.”

### Runtime behavior spec

| Dimension | Recommended behavior |
|---|---|
| Speaking style | Warm, low-pressure, calm, steady |
| Response openers | “Of course.” “Right.” “I hear you.” “Okay.” |
| Pause before empathy | 800–1200ms |
| Pause after questions | ~400ms |
| Endpointing after caller speech | 600–900ms depending on distress level |
| Distress endpointing | Prefer ~900ms to avoid cutting off trailing speech |
| STT low-confidence repair | Reflect back what was heard before acting |
| Empathy length | Maximum 8 words for pure empathy statements |
| Question rule | Never stack questions |
| Silence handling | Wait at least 4 seconds, then say only “I’m still here.” |

### Why this matters

Most teams over-focus on TTS quality and under-focus on conversational behavior. For this challenge, human-pass rate depends heavily on turn-taking, acknowledgment patterns, transition smoothness, and whether the agent behaves like a present claims handler rather than an automated intake form.

## New section: end-to-end conversation phases

The call should be modeled as a phase-based state machine with explicit transition rules. Each phase has a primary emotional job as well as an operational job.

### Phase 1: safety, presence, and emergency services

**Goal:** establish presence, check physical safety, check whether anyone else is in the car, and determine whether emergency services are needed.

**Never do in this phase:** ask for policy number, claim reference, or identity details; use corporate greeting language first; rush; assume the caller is okay.

**Always do in this phase:** lead with safety, acknowledge silence, check for other passengers, offer emergency help, and allow time.

**Recommended opening:**
- “Hi — I’m here with you. Before anything else, are you in a safe place right now?”
- “Okay. I’m right here. Is anyone else in the car with you — are they okay?”
- “Have emergency services been called yet — police or ambulance? If not, I can stay on the line while you dial 112, or I can send you the number right now. What would help most?”

**State transitions:**
- If urgent ambulance needed → `EMERGENCY_EXIT`
- If caller too distressed to continue → `CALLBACK_PATH`
- If safe enough to proceed → `STORY_LISTENING`

### Phase 2: story and listening

**Goal:** let the caller tell the story in their own words before structured intake begins.

**Behavior rules:** do not interrogate, do not interrupt to clarify too early, use short backchannels, reflect back emotionally important details, and give one final opening before transitioning.

**Recommended opener:**
- “When you’re ready — just tell me what happened. However it comes out is completely fine.”

**Good short empathy examples:**
- “Of course you’re shaking.”
- “That sounds terrifying.”
- “I hear you.”

**Transition rule:** when the narrative naturally slows and the caller has said what feels important, move to `PHOTO_GUIDANCE` if photos matter and it is safe, otherwise to `INFO_GATHERING`.

### Phase 3: photo evidence guidance

**Goal:** capture useful scene evidence before vehicles move, without overwhelming the caller.

**Behavior rules:** ask permission, guide one photo at a time, frame the photos as protecting the caller rather than as insurer evidence collection, and always add “if it’s safe.”

**Recommended transition line:**
- “Before anything gets moved — I’d like to help you take a few photos of the scene. It takes about two minutes and it protects your claim. I’m sending you a text link right now. Is that okay?”

**Photo sequence:**
1. Wide shot of the whole scene.
2. Close-up of damage to the caller’s car.
3. Other vehicle or plate if visible.
4. Street sign or landmark.
5. Optional road conditions or skid marks if safe.

**Fallback rule:** if the caller cannot take photos, reassure them the link stays active and continue the claim.

### Phase 4: information gathering

**Goal:** collect minimum viable FNOL information without sounding like a form.

**Behavior rules:** explicitly signal the transition, ask permission, reassure that missing information is okay, and re-use facts already shared instead of re-asking them.

**Recommended bridge:**
- “What I’d like to do now — if you’re ready — is take down a few details so we can open your claim. It won’t take long, and if you don’t have everything, that’s fine — we can fill gaps later. Shall we?”

**Ask only one thing at a time:**
- policy reference or policyholder name,
- rough incident time,
- location,
- other driver details,
- injury follow-up,
- police involvement.

**Confirmation style:** summarize in plain language before moving on.

### Branch B: callback path

**Goal:** preserve dignity and continuity when the caller cannot continue now.

**Trigger conditions:** long silence, inability to continue, intense distress, crying, confusion, or explicit request to stop.

**Offer:**
- “I can hear this is a lot right now. You don’t have to do this all at once. Can I call you back in 20 minutes — you’d have a moment to breathe, and we’ll pick up exactly where we are. Nothing is lost.”

**Principle:** the claim remains open even with only the phone number and partial evidence. The callback itself is a humanness signal.

### Phase 6: close and next steps

**Goal:** remove uncertainty, explain what happens next, reinforce care, and let the caller end the call.

**Behavior rules:** summarize in plain language, give a specific next-step time window, include medical reminder if injury was mentioned, and never hang up first.

**Recommended close structure:**
1. Summary in ordinary language.
2. Specific next step and time window.
3. Medical reminder if relevant.
4. Affirmation.
5. Open final question.
6. Wait for the caller to end the call.

## New section: updated state machine specification

The architecture should use a hybrid state machine: deterministic states for safety, escalation, callbacks, and mandatory data capture, with flexible language generation inside each state.

### Canonical states

| State | Purpose | Required output | Main next states |
|---|---|---|---|
| CALL_START | Open warmly and check immediate safety | safe_to_talk | SAFETY_CHECK, EMERGENCY_EXIT |
| SAFETY_CHECK | Confirm safety, other passengers, emergency need | safety_status, others_in_car, emergency_needed | STORY_LISTENING, CALLBACK_PATH, EMERGENCY_EXIT |
| STORY_LISTENING | Hear the caller’s own narrative | freeform incident story, emotional cues | PHOTO_GUIDANCE, INFO_GATHERING, CALLBACK_PATH |
| PHOTO_GUIDANCE | Guide evidence capture | photos_requested, sms_sent, photo_progress | INFO_GATHERING, CALLBACK_PATH |
| INFO_GATHERING | Collect minimum claim details | structured FNOL slots | RECAP, CALLBACK_PATH |
| RECAP | Confirm critical facts in plain language | user_confirmed_summary | CLOSE, INFO_GATHERING |
| CLOSE | Explain next steps and end warmly | next_steps_delivered | END |
| CALLBACK_PATH | Pause and resume later without losing progress | callback_time, status_open | END, CALL_START_CALLBACK |
| EMERGENCY_EXIT | Prioritize emergency help over claim handling | emergency_instruction_given | END |
| HUMAN_HANDOFF | Transfer to human support if needed | handoff_status | END |

### Global interrupt rules

These rules can fire from any state:
- If the caller asks for a human → `HUMAN_HANDOFF`
- If the caller needs urgent medical help → `EMERGENCY_EXIT`
- If silence persists beyond threshold → offer `CALLBACK_PATH`
- If STT confidence < 0.75 on a critical field → remain in current state and perform confirmation repair
- If caller becomes too distressed → `CALLBACK_PATH`
- If the caller says they are unsafe on the roadway → shorten flow and prioritize safety, assistance, and callback

### Slot strategy

Use progressive slot filling rather than a rigid questionnaire. The system should extract any slots mentioned naturally in the story phase and only ask for missing high-priority fields later.

**High-priority slots:**
- callback number,
- policy name or reference,
- rough time,
- location,
- other driver present or not,
- injury note,
- drivable status,
- police involvement,
- photo request status.

## New section: system-prompt invariants

These rules should sit above phase-specific instructions in the system prompt and always apply.

1. Every response after caller speech begins with a 1–3 word acknowledgment.
2. Acknowledge emotion before asking for information.
3. Silence is not an error state.
4. Never say the caller is fine or uninjured.
5. Ask one question at a time.
6. Pure empathy statements must be brief.
7. Missing data is acceptable; never make the caller feel they failed.
8. Signal transitions explicitly before moving from emotional to practical tasks.
9. Never hang up first.
10. If asked directly whether this is AI, answer honestly and briefly.
11. If transcription confidence is low, reflect back before taking action.
12. Do not open with company-brand boilerplate when the caller is in distress.

## New section: runtime tuning recommendations

These recommendations convert the conversation script into implementation guidance.

### Voice behavior

- Prefer slightly slower speaking rate than default.
- Prefer steady, low-drama delivery.
- Avoid upward inflection on statements.
- Add occasional micro-hesitation only in longer reflective responses.

### Audio and STT behavior

- Use noise-cleaning or audio enhancement before STT when available.
- Set distress-context endpointing longer than default.
- Use confidence-based repair when STT is uncertain.
- Avoid silent progression on uncertain transcriptions.

### Messaging and callbacks

Prepare these automated messages:
- emergency number SMS,
- photo upload link SMS,
- callback confirmation SMS,
- missed callback reassurance SMS.

## New section: pitch refinement

A stronger one-line design thesis for the project is:

> Most teams will build a claims bot. This project is designed for the worst 20 minutes of someone’s day, and every part of the call is shaped around that reality.
