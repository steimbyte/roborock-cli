#!/usr/bin/env python3
"""
Roborock CLI - Control your Roborock S7 Pro Ultra

Usage: roborock <command> [args]

All commands return JSON.
  Success: {"success": true, "message": "...", "data": {...}}
  Error:   {"success": false, "error": "..."}

Commands:
  Basic:      start, stop, pause, home, spot
  Status:     status, info, consumables, segments
  Speed:      fan <0-105>, fanspeed, water <1-3000>, mop_mode <0-2>
  Cleaning:   clean_rooms <ids>, clean_zones <zones>
  Other:      identify, reset <consumable>

Environment variables:
  ROBOROCK_HOST     Vacuum IP address
  ROBOROCK_TOKEN    Local token
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path

# Suppress python-miio warnings for unsupported models
logging.getLogger('miio').setLevel(logging.CRITICAL)
logging.getLogger('miio.device').setLevel(logging.CRITICAL)

# Load .env file if present
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

try:
    from miio.integrations.vacuum.roborock import RoborockVacuum
except ImportError as e:
    print(json.dumps({"success": False, "error": f"python-miio not installed: {e}"}))
    sys.exit(1)

# Credentials from environment variables (set in .env or shell)
HOST = os.environ.get("ROBOROCK_HOST", "")
TOKEN = os.environ.get("ROBOROCK_TOKEN", "")

if not HOST or not TOKEN:
    print(json.dumps({"success": False, "error": "ROBOROCK_HOST and ROBOROCK_TOKEN must be set (see .env.example)"}))
    sys.exit(1)

# Room mapping (discovered via trial & error)
ROOM_MAP = {
    16: "Flur",
    17: "Küche",
    18: "Schlafzimmer",
    19: "Badezimmer",
    21: "Wohnzimmer",
}


def cmd_start(args):
    v = get_vacuum()
    v.start()
    print(json.dumps({"success": True, "message": "Vacuum started"}))


def cmd_stop(args):
    v = get_vacuum()
    v.stop()
    print(json.dumps({"success": True, "message": "Vacuum stopped"}))


def cmd_pause(args):
    v = get_vacuum()
    v.pause()
    print(json.dumps({"success": True, "message": "Vacuum paused"}))


def cmd_home(args):
    v = get_vacuum()
    v.home()
    print(json.dumps({"success": True, "message": "Returning to dock"}))


def cmd_spot(args):
    v = get_vacuum()
    v.spot()
    print(json.dumps({"success": True, "message": "Spot cleaning started"}))


def get_vacuum():
    """Create vacuum instance."""
    try:
        return RoborockVacuum(HOST, TOKEN)
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Connection failed: {str(e)}"}))
        sys.exit(1)


def cmd_status(args):
    v = get_vacuum()
    try:
        s = v.status()
        clean_area = float(s.clean_area) if s.clean_area else 0
        clean_time = (
            s.clean_time.total_seconds()
            if hasattr(s.clean_time, "total_seconds")
            else int(s.clean_time)
            if s.clean_time
            else 0
        )
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Status retrieved",
                    "data": {
                        "state": s.state,
                        "state_code": s.state_code,
                        "battery": s.battery,
                        "fanspeed": s.fanspeed,
                        "error_code": s.error_code,
                        "is_on": s.is_on,
                        "is_paused": s.is_paused,
                        "is_water_box_attached": s.is_water_box_attached,
                        "is_water_shortage": s.is_water_shortage,
                        "clean_area_m2": clean_area,
                        "clean_time_sec": clean_time,
                    },
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_info(args):
    v = get_vacuum()
    try:
        info = v.info()
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Info retrieved",
                    "data": {
                        "model": info.model,
                        "firmware_version": info.firmware_version,
                        "hardware_version": info.hardware_version,
                        "mac_address": info.mac_address,
                        "ip_address": info.ip_address,
                    },
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_fan(args):
    v = get_vacuum()
    level = args.level
    if not 0 <= level <= 105:
        print(json.dumps({"success": False, "error": "Fan level must be 0-105"}))
        return
    try:
        v.set_fan_speed(level)
        print(json.dumps({"success": True, "message": f"Fan speed set to {level}"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_fanspeed(args):
    v = get_vacuum()
    try:
        s = v.status()
        print(
            json.dumps(
                {
                    "success": True,
                    "message": f"Current fan speed: {s.fanspeed}",
                    "fanspeed": s.fanspeed,
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_water(args):
    v = get_vacuum()
    level = args.level
    if not 1 <= level <= 3000:
        print(json.dumps({"success": False, "error": "Water level must be 1-3000"}))
        return
    try:
        # Use raw command as set_waterflow has typing issues
        v.raw_command("set_water_box_custom_mode", [level])
        print(json.dumps({"success": True, "message": f"Water flow set to {level}"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_mop_mode(args):
    v = get_vacuum()
    mode = args.mode
    if mode not in [0, 1, 2]:
        print(json.dumps({"success": False, "error": "Mode must be 0, 1, or 2"}))
        return
    try:
        result = v.raw_command("set_mop_mode", [mode])
        modes = {0: "off", 1: "low", 2: "high"}
        print(
            json.dumps({"success": True, "message": f"Mop mode set to {modes[mode]}"})
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_clean_rooms(args):
    """Clean specific rooms by segment IDs."""
    v = get_vacuum()
    room_ids_str = args.room_ids

    try:
        segments = [int(x.strip()) for x in room_ids_str.split(",")]
    except ValueError:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "Invalid room IDs. Use comma-separated integers, e.g. '1,2,3'",
                }
            )
        )
        return

    try:
        result = v.segment_clean(segments)
        names = [ROOM_MAP.get(s, f"Room {s}") for s in segments]
        print(
            json.dumps(
                {
                    "success": True,
                    "message": f"Cleaning rooms: {', '.join(names)}",
                    "segments": segments,
                    "segment_names": names,
                    "result": str(result),
                }
            )
        )
    except Exception as e:
        print(
            json.dumps({"success": False, "error": f"Room cleaning failed: {str(e)}"})
        )


def cmd_go_room(args):
    """Go to a specific room/segment (for mapping)."""
    v = get_vacuum()
    room_id = int(args.room_id)

    try:
        # segment_clean - just go to room and clean
        result = v.segment_clean([room_id])
        print(
            json.dumps(
                {
                    "success": True,
                    "message": f"Going to room {room_id}",
                    "room_id": room_id,
                    "result": str(result),
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": f"Go room failed: {str(e)}"}))


def cmd_clean_zones(args):
    """Clean zones - [[x1,y1,x2,y2,iterations],...]"""
    v = get_vacuum()
    zones_str = args.zones

    try:
        import ast

        zones = ast.literal_eval(zones_str)
    except Exception:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "Invalid zone format. Use: '[[x1,y1,x2,y2,iter],...]'",
                }
            )
        )
        return

    try:
        result = v.zoned_clean(zones)
        print(
            json.dumps(
                {
                    "success": True,
                    "message": f"Zone cleaning started: {zones}",
                    "zones": zones,
                    "result": str(result),
                }
            )
        )
    except Exception as e:
        print(
            json.dumps({"success": False, "error": f"Zone cleaning failed: {str(e)}"})
        )


def cmd_identify(args):
    v = get_vacuum()
    try:
        v.find()
        print(
            json.dumps({"success": True, "message": "Vacuum identified (sound played)"})
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_segments(args):
    """Get room/segment mapping from vacuum map."""
    v = get_vacuum()
    try:
        mapping = v.get_room_mapping()
        # mapping is list of [segment_id, segment_name or type]
        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Room mapping retrieved",
                    "segments": mapping,
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_rooms(args):
    """List all known rooms."""
    print(
        json.dumps(
            {
                "success": True,
                "message": "Rooms listed",
                "rooms": ROOM_MAP,
            }
        )
    )


def cmd_consumables(args):
    """Get consumable status."""
    v = get_vacuum()
    try:
        c = v.consumable_status()

        # Convert timedelta to hours (clamp to 0-100 for percentages)
        def to_hours(td):
            if hasattr(td, 'total_seconds'):
                val = td.total_seconds() / 3600
                return max(0, round(val, 1))  # Prevent negative hours
            return 0

        def pct(left, total):
            if total:
                val = left / total * 100
                return max(0, min(100, round(val, 1)))  # Clamp 0-100
            return 0

        print(
            json.dumps(
                {
                    "success": True,
                    "message": "Consumables retrieved",
                    "data": {
                        "main_brush_left_hours": to_hours(c.main_brush_left),
                        "main_brush_left_percent": pct(c.main_brush_left, c.main_brush_total),
                        "side_brush_left_hours": to_hours(c.side_brush_left),
                        "side_brush_left_percent": pct(c.side_brush_left, c.side_brush_total),
                        "filter_left_percent": pct(c.filter_left, c.filter_total),
                        "sensor_dirty_hours": to_hours(c.sensor_dirty_left),
                    },
                }
            )
        )
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def cmd_reset(args):
    """Reset consumable timer."""
    v = get_vacuum()
    consumable = args.consumable

    valid = ["main_brush", "side_brush", "filter", "sensor_dirty"]
    if consumable not in valid:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": f"Invalid consumable. Choose: {', '.join(valid)}",
                }
            )
        )
        return

    try:
        v.consumable_reset(consumable)
        print(json.dumps({"success": True, "message": f"{consumable} timer reset"}))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))


def main():
    parser = argparse.ArgumentParser(
        description="Roborock S7 Pro Ultra CLI for n8n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Basic commands
    subparsers.add_parser("start", help="Start vacuuming")
    subparsers.add_parser("stop", help="Stop vacuuming")
    subparsers.add_parser("pause", help="Pause vacuuming")
    subparsers.add_parser("home", help="Return to dock")
    subparsers.add_parser("spot", help="Spot cleaning")

    # Status/Info
    subparsers.add_parser("status", help="Get vacuum status")
    subparsers.add_parser("info", help="Get device info")
    subparsers.add_parser("segments", help="Get room mapping")
    subparsers.add_parser("rooms", help="List known rooms")
    subparsers.add_parser("consumables", help="Get consumable status")

    # Fan/Water
    p_fan = subparsers.add_parser("fan", help="Set fan speed (0-105)")
    p_fan.add_argument("level", type=int, help="Fan level")

    subparsers.add_parser("fanspeed", help="Get current fan speed")

    p_water = subparsers.add_parser("water", help="Set water flow (1-3000)")
    p_water.add_argument("level", type=int, help="Water level")

    p_mop = subparsers.add_parser(
        "mop_mode", help="Set mop mode (0=off, 1=low, 2=high)"
    )
    p_mop.add_argument("mode", type=int, choices=[0, 1, 2], help="Mop mode")

    # Room/Zone
    p_rooms = subparsers.add_parser("clean_rooms", help="Clean rooms by segment IDs")
    p_rooms.add_argument("room_ids", help="Comma-separated IDs, e.g. '1,2,3'")

    p_go = subparsers.add_parser("go_room", help="Go to room (for mapping)")
    p_go.add_argument("room_id", type=int, help="Room segment ID")

    p_zones = subparsers.add_parser("clean_zones", help="Clean zones")
    p_zones.add_argument("zones", help='Zone array: "[[x1,y1,x2,y2,iter],...]"')

    # Maintenance
    subparsers.add_parser("identify", help="Play sound to find vacuum")

    p_reset = subparsers.add_parser("reset", help="Reset consumable timer")
    p_reset.add_argument(
        "consumable",
        choices=["main_brush", "side_brush", "filter", "sensor_dirty"],
        help="Consumable to reset",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print(json.dumps({"success": False, "error": "No command specified"}))
        sys.exit(1)

    commands = {
        "start": cmd_start,
        "stop": cmd_stop,
        "pause": cmd_pause,
        "home": cmd_home,
        "spot": cmd_spot,
        "status": cmd_status,
        "info": cmd_info,
        "fan": cmd_fan,
        "fanspeed": cmd_fanspeed,
        "water": cmd_water,
        "mop_mode": cmd_mop_mode,
        "clean_rooms": cmd_clean_rooms,
        "go_room": cmd_go_room,
        "clean_zones": cmd_clean_zones,
        "identify": cmd_identify,
        "segments": cmd_segments,
        "rooms": cmd_rooms,
        "consumables": cmd_consumables,
        "reset": cmd_reset,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        print(
            json.dumps({"success": False, "error": f"Unknown command: {args.command}"})
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
