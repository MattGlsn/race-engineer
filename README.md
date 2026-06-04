# Race Engineer

A real-time pit-wall assistant for [iRacing](https://www.iracing.com/). A Python **bridge** reads live session data from the iRacing SDK, answers questions over push-to-talk voice, and streams race state to a React **desktop** dashboard.

## What it does

- **Live race data** — Gaps ahead and behind, position, lap timing, fuel use, and finish-fuel projections while you are on track.
- **Voice engineer** — Hold a push-to-talk hotkey (or a steering-wheel button) on the machine running the bridge; your question is transcribed, answered with current session context, and spoken back on that machine’s speakers.
- **Dashboard** — A browser UI shows connection health, live widgets, and a transcript of driver and engineer messages.
- **Configurable radio style** — Engineer tone (calm, direct, intense), hotkey, and playback volume are adjustable from the desktop and stored on the bridge.

Voice capture and playback always run on the **bridge** computer (where iRacing and the microphone live). The desktop is a separate display and control panel; it does not record or play audio itself.

## Project layout

| Folder | Role |
|--------|------|
| [`bridge/`](bridge/) | Python telemetry bridge, FastAPI server, iRacing SDK connection, voice pipeline |
| [`desktop/`](desktop/) | React + Vite dashboard (connects to the bridge over WebSocket) |

For HTTP/WebSocket API details and developer setup, see [`bridge/README.md`](bridge/README.md) and [`desktop/README.md`](desktop/README.md).

## Prerequisites

- **iRacing** installed and able to launch a session (practice, qualify, or race).
- **Python 3.10+** for the bridge.
- **Node.js 20+** for the desktop (development or local preview).
- **API keys** (optional but required for full voice):
  - [ElevenLabs](https://elevenlabs.io/) — speech-to-text and text-to-speech (`ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID`)
  - [OpenAI](https://platform.openai.com/) — engineer replies (`OPENAI_API_KEY`)

Run the bridge on the same PC as iRacing so the SDK and your microphone are available.

## Launch

### 1. Configure the bridge (first time)

```bash
cd bridge
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -e ".[dev]"
```

Create `bridge/.env` with your keys (minimum for push-to-talk):

```env
ELEVENLABS_API_KEY=your_key
ELEVENLABS_VOICE_ID=your_voice_id
OPENAI_API_KEY=your_key
```

Other useful variables (hotkey, volume, joystick PTT) are documented in [`bridge/README.md`](bridge/README.md).

### 2. Start iRacing

Load into a session so the iRacing SDK is active (garage or on track).

### 3. Start the bridge

```bash
cd bridge
# activate .venv if needed
uvicorn race_engineer.api.app:app --reload
```

The API listens at `http://127.0.0.1:8000`. Check `GET http://127.0.0.1:8000/health` or open `http://127.0.0.1:8000/docs`.

### 4. Start the desktop

In a second terminal:

```bash
cd desktop
npm install
npm run dev
```

Open **http://localhost:5173** (layout is tuned for 1080p).

Status cards at the top should show **Bridge → Connected**, then **iRacing SDK → Connected** once the sim is linked. **Race state** updates when live data is flowing.

## How to use

### Dashboard

The default **Dashboard** view shows four live panels when data is available:

- **Gap** — Time and distance to the car ahead and behind.
- **Position** — Overall and class position in the field.
- **Fuel** — Per-lap usage, laps remaining, projected finish fuel, and risk level.
- **Lap timing** — Best lap, lap count, track name, and session type.

If widgets show placeholders, confirm iRacing is in an active session and the SDK status card is connected.

### Talk to the engineer

1. Ensure voice API keys are set in `bridge/.env` and the bridge is running.
2. In the desktop sidebar, set **Push-to-talk hotkey** (default `Ctrl+Shift+Space`). Click **Change hotkey**, then press the key combination you want. Include **Ctrl** or **Shift** so normal typing does not trigger recording.
3. Choose **Engineer tone** — **Calm**, **Direct**, or **Intense** — to shape how replies are phrased.
4. On the **bridge machine**, **hold** the hotkey (or a configured steering-wheel button via `VOICE_JOYSTICK_PTT` in `.env`) and speak. **Release** to send.
5. The bridge transcribes your message, builds context from live telemetry, generates a short reply, plays it on the bridge speakers, and sends both sides of the conversation to the desktop.

The app switches to **Transcript** when a new message arrives. Use **Engineer volume** on that screen (0–200%) if replies are hard to hear over engine noise; playback gain is applied on the bridge.

While you are holding the hotkey, the transcript view shows a **recording** indicator when the bridge reports capture in progress.

Example questions the system is built around: fuel strategy, gaps, position, lap time, and general coaching — answers use whatever session data is available at that moment.

### Transcript

Open **Transcript** in the sidebar to browse past conversations (stored in the browser), read driver and engineer lines, and adjust engineer volume. Conversations are grouped by session; select one in the list to read its messages.

### Steering-wheel push-to-talk (optional)

To use a wheel or gamepad button instead of (or as well as) the keyboard, set `VOICE_JOYSTICK_PTT` in `bridge/.env`. Discover device and button indices:

```bash
cd bridge
python -m race_engineer.voice.hotkey.discover_joystick
```

See [`bridge/README.md`](bridge/README.md) for binding examples (`12`, `1:12`, `0:axis:4`, etc.).

## Troubleshooting

| Symptom | What to check |
|---------|----------------|
| Bridge disconnected in the UI | Bridge not running, or wrong host/port (default `ws://127.0.0.1:8000/ws`) |
| SDK not connected | iRacing not running or not in a session |
| No race data in widgets | SDK connected but not on track / session not reporting |
| Hotkey does nothing | Keys only work on the bridge PC; bridge must be running with ElevenLabs configured |
| Transcript updates, no audio | `ELEVENLABS_VOICE_ID` set; volume on Transcript view; Windows default output device |
| Engineer errors in transcript | Missing `OPENAI_API_KEY` or `ELEVENLABS_VOICE_ID` after a successful transcription |

## Development

```bash
# Bridge tests
cd bridge
python -m pytest tests/ -v

# Desktop lint / build
cd desktop
npm run lint
npm run build
```
