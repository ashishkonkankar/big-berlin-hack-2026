# INCA Insurance Voice Agent (Hackathon MVP)

This is a practical MVP for the INCA roadside FNOL voice workflow:
- inbound call webhook for claims intake,
- structured slot-filling state machine,
- SMS secure upload link,
- photo upload endpoint,
- image finding stub,
- claims JSON API + dashboard.

## What this ships

- `POST /twilio/voice` starts a call session and asks opening safety question.
- `POST /twilio/voice/process` processes speech, updates FNOL fields, and asks the next question.
- `GET /upload/:token` shows a secure upload page.
- `POST /upload/:token` accepts an image and appends image findings.
- `GET /claims` returns all claims in JSON.
- `GET /dashboard` returns a simple internal claims dashboard.
- `GET /integrations/gradium` returns whether `GRADIUM_API_KEY` is configured.
- `GET /integrations/gemini` returns whether `GEMINI_API_KEY` is configured.
- `POST /agent/respond` asks Gemini for the next phase-aware agent decision.
- `POST /gradium/events` ingests realtime call events from a Gradium-side orchestrator.
- `POST /gradium/tts` returns Gradium-generated audio for agent speech.
- `WS /gradium/asr` proxies browser microphone PCM to Gradium realtime ASR/STT.
- `GET /monitor` serves the minimal live call monitor.
- `GET /events` streams live claim snapshots to the monitor via server-sent events.

## Quick start

```bash
npm install
cp .env.example .env
npm run dev
```

Server defaults to `http://localhost:8080`.

If port 8080 is already taken:

```bash
PORT=8092 PUBLIC_BASE_URL=http://localhost:8092 npm start
```

Open the live monitor at:

```text
http://localhost:8092/monitor
```

## Twilio setup

1. Buy/choose a Twilio number with voice + SMS.
2. Expose local server using ngrok or cloud deploy.
3. Set Twilio voice webhook to:
   - `https://<public-url>/twilio/voice` (HTTP POST)
4. Set `.env`:
   - `PUBLIC_BASE_URL=https://<public-url>`
   - `TWILIO_ACCOUNT_SID=...`
- `TWILIO_AUTH_TOKEN=...`
- `TWILIO_FROM_NUMBER=+...`
- `GRADIUM_API_KEY=...`
- `GRADIUM_VOICE_ID=apU2CMobTyu92tZj`
- `GEMINI_API_KEY=...`
- `GEMINI_MODEL=gemini-2.5-flash`

If Twilio env vars are missing, SMS sends are mocked and printed in server logs.

## Data storage

- Claims are stored in `data/claims.json`.
- Uploaded files are stored in `uploads/`.

## Notes

- This repo currently uses Twilio TTS voice in TwiML for speed of integration.
- To integrate Gradium/Gemini as in your brief:
  1. replace TwiML speech loop with realtime media streaming + barge-in,
  2. route utterances into LLM policy for response generation,
  3. replace image stub with true multimodal analysis.

## Gradium event payload examples

The prototype is configured for Gradium voice `apU2CMobTyu92tZj` (`Daniel`), a smooth Australian masculine conversational voice available in the Gradium catalog.

The monitor uses Gradium in two places:
- TTS: browser calls `POST /gradium/tts`; backend calls Gradium with `voice_id`.
- ASR/STT: browser streams 24kHz PCM over `WS /gradium/asr`; backend forwards it to Gradium with `x-api-key`.

The monitor uses Gemini as the dialogue brain:
- browser sends caller text, recent transcript, and memory to `POST /agent/respond`;
- backend asks Gemini for structured JSON with the next response, phase, memory patch, and claim patch;
- browser applies the decision and sends the response to Gradium TTS.

```bash
curl -X POST http://localhost:8080/gradium/events \
  -H "Content-Type: application/json" \
  -d '{"type":"caller_transcript","callId":"CALL-123","text":"I was hit near Alexanderplatz."}'
```

```bash
curl -X POST http://localhost:8080/gradium/events \
  -H "Content-Type: application/json" \
  -d '{"type":"field","callId":"CALL-123","field":"incidentLocation","value":"Alexanderplatz"}'
```
