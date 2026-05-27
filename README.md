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

### Basic
| Command | Beschreibung |
|---------|--------------|
| `start` | Vollständige Reinigung starten |
| `stop` | Reinigung stoppen |
| `pause` | Pause |
| `home` | Zur Ladestation |
| `spot` | Spot-Reinigung |

### Status
| Command | Beschreibung |
|---------|--------------|
| `status` | Aktueller Status (Akku, Zustand) |
| `info` | Geräte-Infos (Modell, Firmware) |
| `consumables` | Verbrauchsmaterialien-Status |
| `history` | Reinigungshistorie |
| `timers` | Geplante Timer |

### Fan Speed
| Command | Beschreibung |
|---------|--------------|
| `fans silent` | Leise |
| `fans standard` | Normal |
| `fans medium` | Mittel |
| `fans turbo` | Turbo |
| `fans gentle` | Schonend |
| `fans auto` | Automatisch |
| `fanspeed` | Zeigt aktuelle Stufe + alle Presets |

### Water/Mop
| Command | Beschreibung |
|---------|--------------|
| `water <1-3000>` | Wasserfluss einstellen |
| `mop_mode <0-2>` | Mop-Modus (0=aus, 1=niedrig, 2=hoch) |

### Cleaning
| Command | Beschreibung |
|---------|--------------|
| `clean_rooms 17,18` | Bestimmte Räume reinigen |
| `clean_zones "[[x1,y1,x2,y2,iter],...]"` | Zonen reinigen |
| `goto <x> <y>` | Zu Koordinaten fahren |

### Settings
| Command | Beschreibung |
|---------|--------------|
| `dnd` | DND-Status anzeigen |
| `dnd_set on 22:00 08:00` | DND aktivieren |
| `dnd_set off` | DND deaktivieren |
| `carpet` | Teppichmodus-Status |
| `carpet_set on` | Teppichmodus an |
| `carpet_set off` | Teppichmodus aus |
| `childlock status` | Kindersicherung-Status |
| `childlock on` | Kindersicherung an |
| `childlock off` | Kindersicherung aus |
| `volume` | Lautstärke anzeigen |
| `set_volume <0-100>` | Lautstärke setzen |

### Maintenance
| Command | Beschreibung |
|---------|--------------|
| `identify` | Signalton abspielen |
| `reset main_brush` | Hauptbürste zurücksetzen |
| `reset side_brush` | Seitenbürste zurücksetzen |
| `reset filter` | Filter zurücksetzen |
| `reset sensor_dirty` | Sensor zurücksetzen |

### Info
| Command | Beschreibung |
|---------|--------------|
| `segments` | Raum-Segment-Mapping |
| `rooms` | Bekannte Räume |

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
python /pfad/roborock_cli.py fans turbo
```

Alle Commands geben JSON zurück:
```json
{"success": true, "message": "...", "data": {...}}
```
