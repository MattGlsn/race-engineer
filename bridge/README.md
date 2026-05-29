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
- Interactive docs: `http://127.0.0.1:8000/docs`

Optional: set `CORS_ORIGINS` (comma-separated) to override default localhost origins.

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
