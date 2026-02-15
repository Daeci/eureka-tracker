# Eureka Moment Tracker

Track [Eureka Moment](https://ffxiv.consolegameswiki.com/wiki/Eureka_Moment) proc rates from **Solid Reason** (Miner) and **Ageless Words** (Botanist) in Final Fantasy XIV.

Connects to [IINACT](https://github.com/marzent/IINACT)'s WebSocket for real-time game event data — counters update instantly as you gather.

## Features

- Live tracking of Solid Reason and Ageless Words usage
- Eureka Moment proc counter with proc rate percentage
- Dark-themed UI
- Auto-reconnects if IINACT disconnects

## Requirements

- [IINACT](https://github.com/marzent/IINACT) Dalamud plugin with WebSocket server enabled (default: `ws://127.0.0.1:10501/ws`)
- Python 3.10+
- [websocket-client](https://pypi.org/project/websocket-client/)

## Setup

```bash
pip install websocket-client
python eureka_tracker.py
```

## Usage

1. Launch FFXIV with Dalamud and ensure IINACT is running
2. Run `eureka_tracker.py`
3. Click **Start**
4. Use Solid Reason or Ageless Words while gathering — counters update in real-time
5. Click **Reset** to zero out counters for a new session
