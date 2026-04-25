"""INCA Track voice claims agent using Gradbot."""

from __future__ import annotations

import json
import os
import pathlib
from dataclasses import asdict, dataclass
from typing import Any

import fastapi
import gradbot


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_DIR = pathlib.Path(__file__).resolve().parent
DEFAULT_VOICE_ID = "apU2CMobTyu92tZj"


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
os.environ.setdefault(
    "LLM_BASE_URL",
    "https://generativelanguage.googleapis.com/v1beta/openai",
)
os.environ.setdefault("LLM_MODEL", os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
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
        ]
        return "\n".join(rows)


def read_prompt(name: str) -> str:
    return (APP_DIR / "prompts" / name).read_text().strip()


BASE_PROMPT = read_prompt("base.txt")


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
]


def make_instructions(state: ClaimState) -> str:
    return (
        f"{BASE_PROMPT}\n\n"
        "Current live claim state. Use this memory. Do not ask again for filled facts.\n"
        f"{state.summary()}"
    )


def make_config(state: ClaimState, speaks_first: bool = False, speed: float = 0.9) -> gradbot.SessionConfig:
    voice_id = os.environ.get("GRADIUM_VOICE_ID", DEFAULT_VOICE_ID)
    speed = max(0.5, min(1.4, float(speed or 0.9)))
    kwargs = {
        "assistant_speaks_first": speaks_first,
        "silence_timeout_s": 0.0,
        "rewrite_rules": "en",
        "padding_bonus": 1.2 + max(0.0, 1.0 - speed),
        "flush_duration_s": 1.6,
        "stt_extra_config": json.dumps({"delay_in_frames": 48}),
    } | cfg.session_kwargs
    kwargs["assistant_speaks_first"] = speaks_first
    kwargs["silence_timeout_s"] = 0.0
    kwargs["flush_duration_s"] = 1.6
    kwargs["stt_extra_config"] = json.dumps({"delay_in_frames": 48})

    return gradbot.SessionConfig(
        voice_id=voice_id,
        language=gradbot.Lang.En,
        instructions=make_instructions(state),
        tools=TOOLS,
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

    await handle.send_error(f"Unknown tool: {handle.name}")


@app.get("/api/claim-start")
async def claim_start():
    return {"state": ClaimState().public(), "voice_id": os.environ.get("GRADIUM_VOICE_ID", DEFAULT_VOICE_ID)}


@app.websocket("/ws/chat")
async def ws_chat(websocket: fastapi.WebSocket):
    state = ClaimState()

    async def on_start(msg: dict) -> gradbot.SessionConfig:
        await send_state(websocket, state, "claim_start")
        return make_config(state, speaks_first=True, speed=msg.get("speed", 0.9))

    async def on_config(msg: dict) -> gradbot.SessionConfig:
        return make_config(state, speaks_first=False, speed=msg.get("speed", 0.9))

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
)
