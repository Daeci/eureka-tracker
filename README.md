# Eureka Moment Tracker

Track Eureka Moment effect proc rates from **Solid Reason** (Miner) and **Ageless Words** (Botanist) in Final Fantasy XIV.

Connects to [IINACT](https://github.com/marzent/IINACT)'s WebSocket for real-time game event data — counters update instantly as you gather.

## Features

- Live tracking of Solid Reason and Ageless Words usage
- Eureka Moment proc counter with proc rate percentage
- Dark-themed UI
- Auto-reconnects if IINACT disconnects

## Download

Grab the latest `EurekaMomentTracker.exe` from the [Releases](https://github.com/Daeci/eureka-tracker/releases) page — no Python installation required.

### Requirements

- [IINACT](https://github.com/marzent/IINACT) Dalamud plugin with WebSocket server enabled

### Usage

1. Launch FFXIV with Dalamud and ensure IINACT is running
2. Run `EurekaMomentTracker.exe`
3. Click **Start**
4. Use Solid Reason or Ageless Words while gathering — counters update in real-time
5. Click **Reset** to zero out counters for a new session

## Running from Source

Requires Python 3.10+ and [websocket-client](https://pypi.org/project/websocket-client/).

```bash
pip install websocket-client
python eureka_tracker.py
```

### Building the Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name EurekaMomentTracker eureka_tracker.py
```

The executable will be in the `dist/` folder.
