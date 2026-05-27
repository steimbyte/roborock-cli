# Roborock CLI

CLI Tool zur Steuerung des Roborock S7 Pro Ultra.

## Setup

```bash
# .env Datei erstellen
cp .env.example .env

# Token eintragen
# ROBOROCK_HOST=192.168.178.21
# ROBOROCK_TOKEN=DEIN_TOKEN

# python-miio installieren
pip install python-miio python-dotenv

# Ausführen
python roborock_cli.py status
```

## Commands

| Command | Beschreibung |
|---------|--------------|
| `status` | Aktueller Status (Akku, Zustand) |
| `info` | Geräte-Infos (Modell, Firmware) |
| `start` | Vollständige Reinigung starten |
| `stop` | Reinigung stoppen |
| `pause` | Pause |
| `home` | Zur Ladestation |
| `spot` | Spot-Reinigung |
| `clean_rooms 17,18` | Bestimmte Räume reinigen |
| `consumables` | Verbrauchsmaterialien-Status |
| `identify` | Signalton abspielen |

## Room Mapping

| Segment | Raum |
|---------|------|
| 16 | Flur |
| 17 | Küche |
| 18 | Schlafzimmer |
| 19 | Badezimmer |
| 21 | Wohnzimmer |

## Environment Variables

```bash
ROBOROCK_HOST=192.168.178.21
ROBOROCK_TOKEN=DEIN_TOKEN
```

## n8n Integration

```bash
# Im Execute Command Node
python /pfad/roborock_cli.py status
python /pfad/roborock_cli.py clean_rooms 17,18
```

Alle Commands geben JSON zurück:
```json
{"success": true, "message": "...", "data": {...}}
```
