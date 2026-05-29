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
- Interactive docs: `http://127.0.0.1:8000/docs`

Optional environment:

- `CORS_ORIGINS` (comma-separated) to override default localhost origins
- `ELEVENLABS_STT_MODEL`, `ELEVENLABS_TTS_MODEL`, `ELEVENLABS_TTS_OUTPUT_FORMAT` (default `pcm_16000`)
- `VOICE_OUTPUT_VOLUME` (0.0–1.0, default `1.0`)
- `VOICE_HOTKEY` (default `ctrl+shift+space`) — global push-to-talk while the bridge is running; hold to record, release to transcribe and push a `transcript` message to WebSocket clients

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
