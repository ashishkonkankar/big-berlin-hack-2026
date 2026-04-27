"""INCA Track voice claims agent using Gradbot."""

from __future__ import annotations

import asyncio
import json
import os
import pathlib
import urllib.request
import urllib.error
from dataclasses import asdict, dataclass, field
from typing import Any

import fastapi
import gradbot


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_VOICE_ID = "56DcpvEI0Gawpidh"


def load_env_file(path: pathlib.Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


load_env_file(ROOT / ".env")
if os.environ.get("GEMINI_API_KEY") and not os.environ.get("LLM_API_KEY"):
    os.environ["LLM_API_KEY"] = os.environ["GEMINI_API_KEY"]
try:
    from dotenv import load_dotenv
    load_dotenv(APP_DIR.parent / ".env")
    load_dotenv(APP_DIR / ".env")
except ImportError:
    pass

os.environ.setdefault(
    "LLM_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai",
)
os.environ.setdefault("LLM_MODEL", os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite"))
os.environ.setdefault("CONFIG_DIR", str(APP_DIR))

gradbot.init_logging()
app = fastapi.FastAPI(title="INCA Track Gradbot")
cfg = gradbot.config.from_env()


@dataclass
class ClaimState:
    phase: str = "1 Safety and Presence"
    policyholder: str = "-"
    policy_number: str = "-"
    vehicle: str = "-"
    coverage: str = "-"
    safe_place: str = "-"
    emergency_services: str = "-"
    time_of_incident: str = "-"
    location: str = "-"
    damage_description: str = "-"
    other_party: str = "-"
    injury_noted: str = "-"
    photos_received: int = 0
    photo_link_sent: bool = False
    police_report: str = "-"
    callback_requested: bool = False
    claim_complete: bool = False
    agent_state: str = "Call ready"
    nearest_hospital: str = "-"
    nearest_police: str = "-"

    def public(self) -> dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        rows = [
            f"phase: {self.phase}",
            f"policyholder: {self.policyholder}",
            f"policy_number: {self.policy_number}",
            f"vehicle: {self.vehicle}",
            f"coverage: {self.coverage}",
            f"safe_place: {self.safe_place}",
            f"emergency_services: {self.emergency_services}",
            f"time_of_incident: {self.time_of_incident}",
            f"location: {self.location}",
            f"damage_description: {self.damage_description}",
            f"other_party: {self.other_party}",
            f"injury_noted: {self.injury_noted}",
            f"photos_received: {self.photos_received}",
            f"photo_link_sent: {self.photo_link_sent}",
            f"police_report: {self.police_report}",
            f"callback_requested: {self.callback_requested}",
            f"claim_complete: {self.claim_complete}",
            f"nearest_hospital: {self.nearest_hospital}",
            f"nearest_police: {self.nearest_police}",
        ]
        return "\n".join(rows)


def tavily_search(query: str, max_results: int = 1) -> str:
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        return "-"
    try:
        body = json.dumps(
            {
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
                "include_answer": True,
            }
        ).encode()
        req = urllib.request.Request(
            "https://api.tavily.com/search",
            data=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        answer = (data.get("answer") or "").strip()
        if answer:
            return answer[:240]
        results = data.get("results") or []
        if results:
            top = results[0]
            return (top.get("title") or top.get("content") or "-")[:240]
        return "-"
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return "-"


async def lookup_support(location: str) -> dict[str, str]:
    if not location or location.strip() in ("", "-"):
        location = "Berlin Mitte"
    loop = asyncio.get_running_loop()
    hospital_q = f"closest hospital with emergency room near {location}, name and street address only"
    police_q = f"closest police station near {location}, name and street address only"
    hospital, police = await asyncio.gather(
        loop.run_in_executor(None, tavily_search, hospital_q),
        loop.run_in_executor(None, tavily_search, police_q),
    )
    return {"nearest_hospital": hospital, "nearest_police": police}


def read_prompt(name: str) -> str:
    return (APP_DIR / "prompts" / name).read_text().strip()


# Prompts are read fresh per session so edits go live without a server restart.


TOOLS = [
    gradbot.ToolDef(
        name="update_claim_record",
        description="Update the live claim record when the caller provides a fact or when the conversation phase changes.",
        parameters_json=json.dumps(
            {
                "type": "object",
                "properties": {
                    "phase": {"type": "string"},
                    "policyholder": {"type": "string"},
                    "policy_number": {"type": "string"},
                    "vehicle": {"type": "string"},
                    "coverage": {"type": "string"},
                    "safe_place": {"type": "string"},
                    "emergency_services": {"type": "string"},
                    "time_of_incident": {"type": "string"},
                    "location": {"type": "string"},
                    "damage_description": {"type": "string"},
                    "other_party": {"type": "string"},
                    "injury_noted": {"type": "string"},
                    "photos_received": {"type": "integer"},
                    "police_report": {"type": "string"},
                    "agent_state": {"type": "string"},
                },
                "additionalProperties": False,
            }
        ),
    ),
    gradbot.ToolDef(
        name="send_photo_link",
        description="Send the claimant a photo upload link by SMS and mark that the photo link was sent.",
        parameters_json=json.dumps(
            {
                "type": "object",
                "properties": {
                    "agent_state": {"type": "string"},
                },
                "additionalProperties": False,
            }
        ),
    ),
    gradbot.ToolDef(
        name="request_callback",
        description="Schedule a callback when the caller cannot continue the claim now.",
        parameters_json=json.dumps(
            {
                "type": "object",
                "properties": {
                    "minutes": {"type": "integer"},
                    "agent_state": {"type": "string"},
                },
                "required": ["minutes"],
                "additionalProperties": False,
            }
        ),
    ),
    gradbot.ToolDef(
        name="complete_claim",
        description="Mark the claim as complete after the closing summary and next steps are handled.",
        parameters_json=json.dumps(
            {
                "type": "object",
                "properties": {
                    "agent_state": {"type": "string"},
                },
                "additionalProperties": False,
            }
        ),
    ),
    gradbot.ToolDef(
        name="end_call",
        description="End the call after the caller has said goodbye or confirmed they're done. Call this only AFTER you've spoken your final goodbye line in the same turn — never before. Do not call if the caller still has questions or is mid-thought.",
        parameters_json=json.dumps(
            {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Short reason e.g. 'caller said goodbye', 'claim closed', 'caller hung up verbally'."},
                },
                "additionalProperties": False,
            }
        ),
    ),
]


def make_instructions(state: ClaimState) -> str:
    base_prompt = read_prompt("base.txt")
    natural_voice = read_prompt("natural_voice.txt")
    return (
        f"{base_prompt}\n\n"
        f"{natural_voice}\n\n"
        "Current live claim state. Use this memory. Do not ask again for filled facts.\n"
        f"{state.summary()}"
    )


def make_config(state: ClaimState, speaks_first: bool = False, speed: float = 1.0) -> gradbot.SessionConfig:
    voice_id = os.environ.get("GRADIUM_VOICE_ID", DEFAULT_VOICE_ID)
    speed = max(0.5, min(1.4, float(speed or 1.0)))
    # Padding shrinks above 1.0, grows mildly below — caller-controlled tempo without going robotic-fast.
    padding_bonus = 0.7 + max(0.0, 1.0 - speed) * 0.3
    kwargs = {
        "assistant_speaks_first": speaks_first,
        "silence_timeout_s": 0.0,
        "rewrite_rules": "en",
        "padding_bonus": padding_bonus,
        "flush_duration_s": 0.5,
        "stt_extra_config": json.dumps({"delay_in_frames": 24}),
        # Probe: try common TTS rate keys. Unknown keys are typically ignored by the underlying engine;
        # if one is honored, perceived speech rate increases above the baked-in voice pace.
        "tts_extra_config": json.dumps({"speed": speed, "speaking_rate": speed, "rate": speed}),
    } | cfg.session_kwargs
    kwargs["assistant_speaks_first"] = speaks_first
    kwargs["silence_timeout_s"] = 0.0
    kwargs["flush_duration_s"] = 0.9
    kwargs["padding_bonus"] = padding_bonus
    kwargs["stt_extra_config"] = json.dumps({"delay_in_frames": 24})
    kwargs["tts_extra_config"] = json.dumps({"speed": speed, "speaking_rate": speed, "rate": speed})

    return gradbot.SessionConfig(
        voice_id=voice_id,
        language=gradbot.Lang.En,
        instructions=make_instructions(state),
        tools=[],
        **kwargs,
    )


async def send_state(websocket: fastapi.WebSocket, state: ClaimState, event: str = "claim_update") -> None:
    await websocket.send_json(
        {
            "type": "event",
            "event": event,
            "state": state.public(),
        }
    )


def set_if_present(state: ClaimState, args: dict[str, Any], name: str) -> None:
    value = args.get(name)
    if value is None or value == "":
        return
    if hasattr(state, name):
        setattr(state, name, value)


async def on_tool_call(state: ClaimState, handle, input_handle, websocket) -> None:
    args = handle.args
    if handle.name == "update_claim_record":
        for field in (
            "phase",
            "policyholder",
            "policy_number",
            "vehicle",
            "coverage",
            "safe_place",
            "emergency_services",
            "time_of_incident",
            "location",
            "damage_description",
            "other_party",
            "injury_noted",
            "police_report",
            "agent_state",
        ):
            set_if_present(state, args, field)
        if isinstance(args.get("photos_received"), int):
            state.photos_received = args["photos_received"]
        await send_state(websocket, state)
        await input_handle.send_config(make_config(state))
        await handle.send_json({"success": True, "state": state.public()})
        return

    if handle.name == "send_photo_link":
        state.photo_link_sent = True
        state.phase = "3 Photo Evidence"
        state.agent_state = args.get("agent_state") or "SMS sent - photo link"
        await send_state(websocket, state, "photo_link_sent")
        await input_handle.send_config(make_config(state))
        await handle.send_json(
            {
                "success": True,
                "message": "Photo link sent by SMS. Photos save automatically as they arrive.",
                "state": state.public(),
            }
        )
        return

    if handle.name == "request_callback":
        state.callback_requested = True
        state.phase = "B Callback"
        minutes = args.get("minutes") or 20
        state.agent_state = args.get("agent_state") or f"Callback scheduled - {minutes} minutes"
        await send_state(websocket, state, "callback_requested")
        await input_handle.send_config(make_config(state))
        await handle.send_json(
            {
                "success": True,
                "message": f"Callback scheduled for {minutes} minutes from now.",
                "state": state.public(),
            }
        )
        return

    if handle.name == "complete_claim":
        state.claim_complete = True
        state.phase = "6 Close"
        state.agent_state = args.get("agent_state") or "Claim complete"
        await send_state(websocket, state, "claim_complete")
        await input_handle.send_config(make_config(state))
        await handle.send_json({"success": True, "state": state.public()})
        return

    if handle.name == "end_call":
        reason = args.get("reason") or "agent ended call"
        state.agent_state = f"Call ended - {reason}"
        await websocket.send_json(
            {
                "type": "event",
                "event": "call_ended",
                "reason": reason,
                "state": state.public(),
            }
        )
        await handle.send_json({"success": True, "state": state.public()})
        return

    await handle.send_error(f"Unknown tool: {handle.name}")


@app.get("/api/claim-start")
async def claim_start():
    return {"state": ClaimState().public(), "voice_id": os.environ.get("GRADIUM_VOICE_ID", DEFAULT_VOICE_ID)}


LOOKUP_QUERIES = {
    "hospital": "closest hospital with emergency room near {loc}, name and street address",
    "police": "closest police station near {loc}, name and street address",
    "tow": "24 hour towing service near {loc}, company name, phone number, and area",
    "rideshare": "taxi or ride service near {loc}, dispatch phone number",
}

LOOKUP_LABELS = {
    "hospital": "Nearest hospital",
    "police": "Nearest police station",
    "tow": "Tow service nearby",
    "rideshare": "Pickup / taxi nearby",
}


EXTRACTION_SCHEMA = [
    "location",
    "time_of_incident",
    "injury",
    "vehicle",
    "other_party",
    "damage",
    "police_report",
    "emergency_services",
    "policyholder name",
    "policy_number",
    "coverage",
]

FIELD_MAP = {
    "location": "location",
    "time_of_incident": "time_of_incident",
    "injury": "injury_noted",
    "vehicle": "vehicle",
    "other_party": "other_party",
    "damage": "damage_description",
    "police_report": "police_report",
    "emergency_services": "emergency_services",
    "policyholder name": "policyholder",
    "policyholder": "policyholder",
    "policy_number": "policy_number",
    "coverage": "coverage",
}


def pioneer_extract(text: str) -> dict[str, str]:
    api_key = os.environ.get("PIONEER_API_KEY", "")
    model_id = os.environ.get("PIONEER_MODEL_ID", "fastino/gliner2-multi-v1")
    if not api_key or not text or len(text) < 4:
        return {}
    try:
        body = json.dumps(
            {
                "model_id": model_id,
                "task": "extract_entities",
                "text": text,
                "schema": EXTRACTION_SCHEMA,
                "threshold": 0.4,
            }
        ).encode()
        req = urllib.request.Request(
            "https://api.pioneer.ai/inference",
            data=body,
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        entities = (data.get("result") or {}).get("entities") or {}
        out: dict[str, str] = {}
        for key, values in entities.items():
            if not values:
                continue
            target = FIELD_MAP.get(key)
            if not target:
                continue
            joined = ", ".join(str(v).strip() for v in values if str(v).strip())
            if joined:
                out[target] = joined
        return out
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError):
        return {}


@app.post("/api/extract")
async def extract(payload: dict[str, Any] | None = fastapi.Body(default=None)):
    text = ((payload or {}).get("text") or "").strip()
    if not text:
        return {"fields": {}}
    loop = asyncio.get_running_loop()
    fields = await loop.run_in_executor(None, pioneer_extract, text)
    return {"fields": fields, "model": os.environ.get("PIONEER_MODEL_ID", "fastino/gliner2-multi-v1")}


@app.post("/api/support-lookup")
async def support_lookup(payload: dict[str, Any] | None = fastapi.Body(default=None)):
    payload = payload or {}
    kind = (payload.get("kind") or "hospital").lower()
    location = payload.get("location") or "Berlin Mitte"
    template = LOOKUP_QUERIES.get(kind, LOOKUP_QUERIES["hospital"])
    query = template.format(loc=location)
    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, tavily_search, query)
    return {
        "kind": kind,
        "label": LOOKUP_LABELS.get(kind, "Lookup"),
        "location": location,
        "answer": answer,
    }


@app.websocket("/ws/chat")
async def ws_chat(websocket: fastapi.WebSocket):
    state = ClaimState()

    async def on_start(msg: dict) -> gradbot.SessionConfig:
        await send_state(websocket, state, "claim_start")
        return make_config(state, speaks_first=True, speed=msg.get("speed", 1.05))

    async def on_config(msg: dict) -> gradbot.SessionConfig:
        return make_config(state, speaks_first=False, speed=msg.get("speed", 1.05))

    await gradbot.websocket.handle_session(
        websocket,
        config=cfg,
        on_start=on_start,
        on_config=on_config,
        on_tool_call=lambda *args: on_tool_call(state, *args),
    )


gradbot.routes.setup(
    app,
    config=cfg,
    static_dir=APP_DIR / "static",
    with_voices=True,
)

# Twilio inbound voice bridge — caller dials the Twilio number, audio is bridged
# into a fresh gradbot session per call.
import twilio_bridge  # noqa: E402

twilio_bridge.register(
    app,
    cfg=cfg,
    state_factory=ClaimState,
    config_factory=lambda state: make_config(state, speaks_first=True, speed=1.05),
    tool_dispatcher=on_tool_call,
)
