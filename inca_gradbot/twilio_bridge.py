"""Twilio Voice <-> gradbot bridge.

Twilio Media Streams ships µ-law 8 kHz; gradbot wants PCM 24 kHz in and emits
PCM 48 kHz out. We resample on the fly using stdlib audioop.
"""
from __future__ import annotations

import asyncio
import audioop  # noqa: deprecated in 3.13, fine on 3.12
import base64
import json
import logging
from typing import Any, Awaitable, Callable

import fastapi
import gradbot
from fastapi import Request, WebSocket, WebSocketDisconnect
from twilio.twiml.voice_response import Connect, VoiceResponse

logger = logging.getLogger(__name__)

TWILIO_RATE = 8000
GRADBOT_IN_RATE = 24000
GRADBOT_OUT_RATE = 48000
TWILIO_FRAME_BYTES = 160  # 20 ms of µ-law @ 8 kHz


class _TwilioWsAdapter:
    """Pretends to be a FastAPI WebSocket for tool dispatchers that call
    `send_json` for panel events. Twilio ignores unknown JSON; we tap a few
    events (call_ended) to drive call termination."""

    def __init__(self, ws: WebSocket, on_call_ended: Callable[[], Awaitable[None]]):
        self._ws = ws
        self._on_call_ended = on_call_ended

    async def send_json(self, payload: dict[str, Any]) -> None:
        if payload.get("event") == "call_ended":
            asyncio.create_task(self._on_call_ended())
        # Drop other panel events — Twilio only cares about media/mark/clear.

    async def send_bytes(self, data: bytes) -> None:
        return None


def register(
    app: fastapi.FastAPI,
    *,
    cfg,
    state_factory: Callable[[], Any],
    config_factory: Callable[[Any], gradbot.SessionConfig],
    tool_dispatcher: Callable[..., Awaitable[None]],
) -> None:
    """Wire /twilio/voice (TwiML) and /twilio/media (Media Streams WS)."""

    @app.post("/twilio/voice")
    async def twilio_voice(request: Request):
        host = request.headers.get("host")
        # Twilio dials our public host; same host serves the WS.
        ws_url = f"wss://{host}/twilio/media"
        vr = VoiceResponse()
        connect = Connect()
        connect.stream(url=ws_url)
        vr.append(connect)
        return fastapi.responses.Response(content=str(vr), media_type="application/xml")

    @app.websocket("/twilio/media")
    async def twilio_media(ws: WebSocket):
        await ws.accept()
        state = state_factory()

        in_state = None  # ratecv state, 8k -> 24k
        out_state = None  # ratecv state, 48k -> 8k
        ulaw_buffer = bytearray()  # for chunked send to Twilio

        input_handle = None
        output_handle = None
        stream_sid: str | None = None
        stop_event = asyncio.Event()

        async def close_call() -> None:
            stop_event.set()
            try:
                await ws.close()
            except Exception:
                pass

        adapter = _TwilioWsAdapter(ws, close_call)

        async def output_loop() -> None:
            nonlocal out_state, ulaw_buffer
            try:
                while not stop_event.is_set():
                    msg = await output_handle.receive()
                    if msg is None:
                        break
                    if msg.msg_type == "audio":
                        pcm48 = bytes(msg.data)
                        pcm8, out_state = audioop.ratecv(
                            pcm48, 2, 1, GRADBOT_OUT_RATE, TWILIO_RATE, out_state
                        )
                        ulaw = audioop.lin2ulaw(pcm8, 2)
                        ulaw_buffer.extend(ulaw)
                        # Ship in 20ms chunks for low latency.
                        while len(ulaw_buffer) >= TWILIO_FRAME_BYTES and stream_sid:
                            chunk = bytes(ulaw_buffer[:TWILIO_FRAME_BYTES])
                            del ulaw_buffer[:TWILIO_FRAME_BYTES]
                            await ws.send_text(
                                json.dumps(
                                    {
                                        "event": "media",
                                        "streamSid": stream_sid,
                                        "media": {"payload": base64.b64encode(chunk).decode()},
                                    }
                                )
                            )
                    elif msg.msg_type == "tool_call":
                        handle = gradbot.websocket.ToolHandle(msg.tool_call_handle, msg.tool_call)

                        async def _safe_tool(h=handle):
                            try:
                                await tool_dispatcher(state, h, input_handle, adapter)
                            except Exception as exc:
                                logger.exception("tool dispatch failed")
                                try:
                                    await h.send_error(str(exc))
                                except Exception:
                                    pass

                        asyncio.create_task(_safe_tool())
                    # other msg types (transcript, event, etc.) — drop
            except Exception:
                logger.exception("twilio output loop error")
            finally:
                stop_event.set()

        try:
            while not stop_event.is_set():
                raw = await ws.receive_text()
                data = json.loads(raw)
                event = data.get("event")

                if event == "connected":
                    continue

                if event == "start":
                    stream_sid = data["start"]["streamSid"]
                    session_cfg = config_factory(state)
                    input_handle, output_handle = await gradbot.run(
                        **cfg.client_kwargs,
                        session_config=session_cfg,
                        input_format=gradbot.AudioFormat.Pcm,
                        output_format=gradbot.AudioFormat.Pcm,
                    )
                    asyncio.create_task(output_loop())
                    logger.info("twilio session started: %s", stream_sid)

                elif event == "media":
                    if input_handle is None:
                        continue
                    payload = base64.b64decode(data["media"]["payload"])
                    pcm8 = audioop.ulaw2lin(payload, 2)
                    pcm24, in_state = audioop.ratecv(
                        pcm8, 2, 1, TWILIO_RATE, GRADBOT_IN_RATE, in_state
                    )
                    await input_handle.send_audio(pcm24)

                elif event == "stop":
                    break

        except WebSocketDisconnect:
            pass
        except Exception:
            logger.exception("twilio media ws error")
        finally:
            stop_event.set()
            if input_handle is not None:
                try:
                    await input_handle.close()
                except Exception:
                    pass
            try:
                await ws.close()
            except Exception:
                pass
            logger.info("twilio session ended: %s", stream_sid)
