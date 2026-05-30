# Race Engineer Bridge

Python telemetry bridge that connects to iRacing via [pyirsdk](https://github.com/kutu/pyirsdk).

## Setup

```bash
cd bridge
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
```

## Tests

```bash
cd bridge
python -m pytest tests/ -v
```

## API

Start the FastAPI server locally:

```bash
cd bridge
uvicorn race_engineer.api.app:app --reload
```

- Health check: `GET http://127.0.0.1:8000/health`
- Live telemetry: `WS ws://127.0.0.1:8000/ws` (JSON messages: `connection`, `telemetry`, `race_state`)
- Voice STT: `POST http://127.0.0.1:8000/voice/transcribe` (WAV upload; requires `ELEVENLABS_API_KEY`)
- Intent router: `POST http://127.0.0.1:8000/voice/route` with JSON `{"text":"..."}` → `intent` (`coaching`, `fuel`, `position`, `gap`, `lap`, or `unknown`)
- Engineer TTS: `POST http://127.0.0.1:8000/voice/speak` with JSON `{"text":"..."}` (requires `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`)
- Engineer AI: `POST http://127.0.0.1:8000/voice/ask` with JSON `{"text":"...", "intent":"fuel"}` (optional intent; requires `OPENAI_API_KEY`)
- Engineer tone: `GET` / `PUT http://127.0.0.1:8000/settings/personality` with JSON `{"mode":"calm"|"direct"|"intense"}` (used by push-to-talk and `/voice/ask`)
- Engineer volume: `GET` / `PUT http://127.0.0.1:8000/settings/volume` with JSON `{"volume":0.0-2.0}` (TTS playback gain on the bridge machine)
- Push-to-talk hotkey: `GET` / `PUT http://127.0.0.1:8000/settings/hotkey` with JSON `{"hotkey":"ctrl+shift+space"}` (global PTT binding on the bridge machine; also adjustable via desktop)
- Interactive docs: `http://127.0.0.1:8000/docs`

Optional environment:

- `CORS_ORIGINS` (comma-separated) to override default localhost origins
- `ELEVENLABS_STT_MODEL`, `ELEVENLABS_TTS_MODEL`, `ELEVENLABS_TTS_OUTPUT_FORMAT` (default `pcm_16000`)
- `VOICE_OUTPUT_VOLUME` (0.0–2.0, default `1.0`; values above `1.0` boost TTS over engine noise; also adjustable via desktop or `GET`/`PUT /settings/volume`)
- `VOICE_HOTKEY` (default `ctrl+shift+space`) — initial push-to-talk binding at bridge startup; also adjustable at runtime via desktop or `GET`/`PUT /settings/hotkey` (see **Push-to-talk conversation** below)
- `VOICE_JOYSTICK_PTT` (optional) — steering wheel / gamepad input for push-to-talk. Examples: `12` (button 12 on device 0), `1:12` (device 1, button 12), `0:axis:4` (device 0, axis 4 positive — common for paddle shifters). Works alongside the keyboard hotkey. Run `python -m race_engineer.voice.hotkey.discover_joystick` to find device/button/axis indices.
- `OPENAI_API_KEY` — enables engineer AI replies via `/voice/ask` and the PTT conversation loop
- `OPENAI_MODEL` (default `gpt-4o-mini`), `OPENAI_BASE_URL`, `LLM_TIMEOUT_SECONDS` (default `8.0`), `LLM_MAX_COMPLETION_TOKENS` (default `150`)

## Push-to-talk conversation

When the bridge is running with `ELEVENLABS_API_KEY` configured, hold the configured push-to-talk hotkey (default `ctrl+shift+space`) or steering-wheel button (`VOICE_JOYSTICK_PTT`) to record from the bridge machine's microphone. On release, the bridge runs the full conversation loop:

1. ElevenLabs STT transcribes the recording
2. Driver transcript is broadcast to WebSocket clients (`role: "driver"`)
3. Live race context is built from iRacing SDK data
4. OpenAI generates a short engineer reply (requires `OPENAI_API_KEY`)
5. Engineer reply is broadcast to WebSocket clients (`role: "engineer"`)
6. ElevenLabs TTS plays the reply on the bridge machine's speakers (requires `ELEVENLABS_VOICE_ID`)

Required environment for the full loop:

- `ELEVENLABS_API_KEY` — STT and TTS
- `ELEVENLABS_VOICE_ID` — TTS playback
- `OPENAI_API_KEY` — LLM replies

If `OPENAI_API_KEY` or `ELEVENLABS_VOICE_ID` is missing after a successful transcript, the driver message is still broadcast and an engineer error message is sent to WebSocket clients (no audio playback).

Individual HTTP endpoints (`/voice/transcribe`, `/voice/ask`, `/voice/speak`) remain available for manual or scripted use.

## Usage

```python
from race_engineer.connection import SdkConnectionService
from race_engineer.sdk import IrSdkWrapper
from race_engineer.telemetry import TelemetryVariableReader, is_valid_snapshot

sdk = IrSdkWrapper()
service = SdkConnectionService(sdk=sdk)
reader = TelemetryVariableReader(sdk=sdk)

if service.connect():
    while service.check_health():
        snapshot = reader.read_snapshot()
        if is_valid_snapshot(snapshot):
            print(snapshot.speed, snapshot.rpm, snapshot.gear)
    service.disconnect()
```

Poll `read_snapshot()` at 20Hz or faster while connected. Each call freezes the SDK
variable buffer, reads Speed, FuelLevel, LapDistPct, Gear, Throttle, Brake,
SteeringWheelAngle, and RPM, then unfreezes. When disconnected, all fields are `None`.
