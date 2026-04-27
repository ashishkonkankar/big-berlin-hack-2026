# Inca Voice — Submission

**An emotionally intelligent voice agent that takes FNOL calls — checks the caller is safe, opens the claim, and dispatches the help they actually need.**

Built for Big Berlin Hack 2026.

---

## The problem

When a driver is stuck in a ditch, bleeding, or watching their car burn, the last thing they should encounter is an IVR menu or a logistics-first call center bot asking "What is your approximate location and a brief description of any injuries?"

First-notice-of-loss (FNOL) calls today are designed for the insurer's data pipeline, not for the human in the worst minutes of their day. The result is callers who feel processed, not helped — and insurers who lose the trust moment that defines the entire claim.

## What we built

**Kate** — a voice-first FNOL agent for Inca Insurance that puts the human before the claim.

When a caller dials in, Kate:

1. **Listens for distress signals** — words like "ditch", "blood", "I'm scared", "I need a minute", or audible distress in tone — and instantly switches register. No tree-walk, no menu, no scripted intake.
2. **Leads with empathy** when distress is real. The first words out of her mouth are an emotional acknowledgment, not a logistics question.
3. **Bundles care into one breath** — safety, emergency services, and immediate help (towing, hospital, callback) — so the caller answers what's actually relevant to them.
4. **Defers the claim when the caller can't focus** — name + city is enough to open a claim. The rest comes later, on a callback at 20 minutes, an hour, or whenever the caller picks.
5. **Detects calm callers too** — someone calling to report a fender-bender from yesterday gets "Of course — tell me what happened," not "I'm really sorry that happened, are you safe?"
6. **Honest about its limits** — Kate can dispatch towing, callbacks, SMS links, hospital and police lookups. She won't pretend to deliver water or food. When the caller asks for something physical, she names what she can actually do.
7. **Ends the call gracefully** — auto-hangs up after the goodbye, with a 4-second buffer so the audio finishes playing.

## What makes it different

- **Bucket triage on every opening turn**: classifies the caller into Distress / Calm Claim / Ambiguous before saying a word. Eliminates the "Are you safe?" loop that plagues every FNOL bot demo.
- **Deferred-claim path**: most insurance bots can't take "I'll come back to this" for an answer. Kate can.
- **Emotional cue priority**: when the caller names a feeling ("I'm shaking", "this is overwhelming"), Kate stops logistics and gives them a full turn of presence — no follow-up question.
- **Capability honesty**: hard-coded rule against fabricating services. The bot would rather acknowledge a need it can't meet than promise a service that doesn't exist.
- **Real telephony**: works through Twilio Voice — caller dials a real phone number, audio is bridged through a custom µ-law ↔ PCM resampler into the gradbot stack.
- **Local simulator**: full Twilio Media Streams protocol mock so the agent can be tested with a laptop mic, no phone or carrier needed.

## Architecture

```
   Caller's phone
        │
        ▼
   Twilio Voice  ──webhook──▶  /twilio/voice  ──TwiML──▶  /twilio/media (WebSocket)
                                                              │
                                                              ▼
                                            µ-law 8 kHz  ◀─ audio bridge ─▶  PCM 24 kHz / 48 kHz
                                                              │
                                                              ▼
                                                       gradbot session
                                                       (STT → LLM → TTS)
                                                              │
                                                              ▼
                                          Tools: claim record, photo link, callback,
                                          complete claim, end call, support lookup
```

**Stack**

- **Voice**: gradbot (Rust-backed Python bindings) for STT/LLM/TTS orchestration
- **LLM**: Gemini 2.5 Flash Lite via OpenAI-compatible API (instruction-tuned for long, conflicting prompts)
- **Telephony**: Twilio Voice + Media Streams
- **Audio bridge**: stdlib `audioop` for µ-law/PCM and rate conversion (8 kHz ↔ 24 kHz ↔ 48 kHz)
- **Server**: FastAPI + uvicorn, single Python process, ~700 LOC application code
- **Tunneling**: ngrok for public webhook URL during demo

## Demo

### Option 1 — real phone call

1. Twilio number: **+1 978 540 8599**
2. Voice webhook: `https://<ngrok>.ngrok-free.dev/twilio/voice` (HTTP POST)
3. Dial the number from any phone
4. Try openers like:
   - *"Hi, I just had an accident, I'm in a ditch and I'm scared"* — should trigger distress mode with empathy lead-in
   - *"Hi Kate, I wanted to report something"* — should NOT trigger distress, stays calm
   - *"I think I want some water"* — should acknowledge the need without fabricating a delivery service

### Option 2 — local simulator (no phone needed)

```bash
cd inca_gradbot
.venv/bin/python simulate_twilio.py
```

Talks to your laptop mic, plays Kate through the speakers, exercises the entire Twilio bridge end-to-end.

## Repo layout

```
big-berlin-hack-2026/
├── inca_gradbot/
│   ├── main.py              # FastAPI app, claim state, tools, ws/chat route
│   ├── twilio_bridge.py     # /twilio/voice + /twilio/media + audio bridge
│   ├── simulate_twilio.py   # Local Twilio Media Streams simulator
│   ├── prompts/
│   │   ├── base.txt         # Distress protocol, triage, phases, honesty rules
│   │   └── natural_voice.txt# Emotional registers, prosody, backchannel
│   ├── static/index.html    # Browser-based demo UI
│   └── config.yaml          # gradbot config (LLM, STT, TTS)
└── .env                     # Twilio credentials (not committed)
```

## What we'd build next

- **Real SMS** wired through Twilio (currently the bot says "SMS sent" but no message goes out)
- **Photo intake**: caller-initiated photo upload via the SMS link, with auto-tagging (vehicle damage, plate, scene)
- **Multilingual triage**: detect language switch mid-call and continue in DE/ES/FR/PT/IT
- **Operator handoff**: warm transfer to a human claims agent with full transcript context
- **Post-call brief**: auto-generated incident summary delivered to the claims team within 60 seconds of hangup
- **Hume EVI integration** for prosody-aware emotion tagging — feed caller affect signals into the prompt to refine register switching

## Team

Ashish Konkankar
