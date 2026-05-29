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

## Usage

```python
from race_engineer.connection import SdkConnectionService

service = SdkConnectionService()
if service.connect():
    print(service.as_dict())
    service.disconnect()
```
