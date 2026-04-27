"""Local Twilio Media Streams simulator.

Pretends to be Twilio: captures laptop mic, streams µ-law 8 kHz over the
exact same WebSocket protocol Twilio uses, plays Kate's reply through the
speakers. No phone, no carrier, no money.

Run from inca_gradbot/ with the server already up on port 8093:

    .venv/bin/python simulate_twilio.py

Talk into the mic. Ctrl-C to quit.
"""
from __future__ import annotations

import asyncio
import audioop
import base64
import json
import signal
import sys
import threading
from typing import Optional

import numpy as np
import sounddevice as sd
import websockets

SR = 8000  # Twilio rate
FRAME_MS = 20
FRAME_SAMPLES = SR * FRAME_MS // 1000  # 160
URI = "ws://localhost:8093/twilio/media"
STREAM_SID = "MZsim000000000000000000000000000000"


async def main() -> None:
    play_buffer = bytearray()
    plock = threading.Lock()
    stop = asyncio.Event()

    print(f"Connecting to {URI} ...", flush=True)
    try:
        ws = await websockets.connect(URI, max_size=None)
    except Exception as exc:
        print(f"Could not connect: {exc}")
        print("Is the server running on port 8093?")
        sys.exit(1)
    print("Connected. Sending Twilio handshake.")

    # Twilio protocol: connected -> start -> stream of media events
    await ws.send(json.dumps({"event": "connected", "protocol": "Call", "version": "1.0.0"}))
    await ws.send(
        json.dumps(
            {
                "event": "start",
                "sequenceNumber": "1",
                "streamSid": STREAM_SID,
                "start": {
                    "streamSid": STREAM_SID,
                    "accountSid": "ACsim",
                    "callSid": "CAsim",
                    "tracks": ["inbound"],
                    "mediaFormat": {
                        "encoding": "audio/x-mulaw",
                        "sampleRate": SR,
                        "channels": 1,
                    },
                },
            }
        )
    )

    loop = asyncio.get_running_loop()
    mic_q: asyncio.Queue[bytes] = asyncio.Queue(maxsize=200)

    def mic_cb(indata, frames, time, status):  # noqa: ARG001
        if status:
            # buffer over/under runs aren't fatal here
            pass
        pcm16 = (indata[:, 0] * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
        ulaw = audioop.lin2ulaw(pcm16, 2)
        try:
            asyncio.run_coroutine_threadsafe(mic_q.put(ulaw), loop)
        except RuntimeError:
            pass

    def spk_cb(outdata, frames, time, status):  # noqa: ARG001
        need = frames * 2
        with plock:
            avail = len(play_buffer)
            take = min(avail, need)
            chunk = bytes(play_buffer[:take])
            del play_buffer[:take]
        if take < need:
            chunk = chunk + b"\x00" * (need - take)
        outdata[:] = np.frombuffer(chunk, dtype=np.int16).reshape(-1, 1)

    in_stream = sd.InputStream(
        samplerate=SR, channels=1, dtype="float32", blocksize=FRAME_SAMPLES, callback=mic_cb
    )
    out_stream = sd.OutputStream(
        samplerate=SR, channels=1, dtype="int16", blocksize=FRAME_SAMPLES, callback=spk_cb
    )
    in_stream.start()
    out_stream.start()
    print("Mic + speakers live. Talk to Kate. Ctrl-C to quit.")

    async def send_loop() -> None:
        seq = 2
        while not stop.is_set():
            try:
                ulaw = await asyncio.wait_for(mic_q.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            try:
                await ws.send(
                    json.dumps(
                        {
                            "event": "media",
                            "sequenceNumber": str(seq),
                            "streamSid": STREAM_SID,
                            "media": {
                                "track": "inbound",
                                "chunk": str(seq),
                                "timestamp": str((seq - 1) * FRAME_MS),
                                "payload": base64.b64encode(ulaw).decode(),
                            },
                        }
                    )
                )
            except websockets.ConnectionClosed:
                stop.set()
                return
            seq += 1

    async def recv_loop() -> None:
        try:
            async for raw in ws:
                if isinstance(raw, bytes):
                    continue
                try:
                    msg = json.loads(raw)
                except Exception:
                    continue
                ev = msg.get("event")
                if ev == "media":
                    payload = base64.b64decode(msg["media"]["payload"])
                    pcm16 = audioop.ulaw2lin(payload, 2)
                    with plock:
                        # cap buffer at ~3s so we don't pile up if interrupted
                        if len(play_buffer) > SR * 2 * 3:
                            del play_buffer[: len(play_buffer) - SR * 2 * 3]
                        play_buffer.extend(pcm16)
                elif ev == "mark":
                    pass
        except websockets.ConnectionClosed:
            pass
        finally:
            stop.set()

    def on_sigint() -> None:
        stop.set()

    loop.add_signal_handler(signal.SIGINT, on_sigint)

    try:
        await asyncio.gather(send_loop(), recv_loop())
    finally:
        in_stream.stop()
        out_stream.stop()
        try:
            await ws.send(json.dumps({"event": "stop", "streamSid": STREAM_SID}))
            await ws.close()
        except Exception:
            pass
        print("\nSession ended.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
