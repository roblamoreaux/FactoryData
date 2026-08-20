import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILENAME = "config.json"

# Built-in fallback defaults. These are used to fill in any keys missing
# from config.json, and to generate a fresh config.json if one doesn't
# exist yet.
DEFAULT_CONFIG = {
    "addresses_file": "Addresses.txt",
    "output_directory": "output",
    "initial_values": {
        "shift": "1",
        "dateMGF": "2026-04-01",
        "Base_PN": "01T070412",
        "issue_mod": "03:00",
        "serialNumber": "",
        "mfg_Location": "   USI",
        "developer_features": "0",
        "PLC_MAC_address": "",
        "PIB_PN": "00 000000",
        "Enet_MAC_Address": "",
        "base_PN_at_MFG": "02T070409",
        "Config_Issue_at_MFG": "1",
        "HW_product_name_Part1": "Nx3-00",
        "HW_product_name_Part2": "0     "
    }
}


def _resolve_path(path):
    """Resolve a possibly-relative path against the script's own directory."""
    if os.path.isabs(path):
        return path
    return os.path.join(SCRIPT_DIR, path)


def load_config(path=None):
    """
    Load config.json (creating a default one next to the script if it
    doesn't exist), merge it over DEFAULT_CONFIG, and resolve
    addresses_file / output_directory into absolute paths.
    """
    config_path = _resolve_path(path or CONFIG_FILENAME)

    # Start from a deep copy of the built-in defaults.
    config = json.loads(json.dumps(DEFAULT_CONFIG))

    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                user_config = json.load(f)
            for k, v in user_config.items():
                if k == "initial_values" and isinstance(v, dict):
                    config["initial_values"].update(v)
                else:
                    config[k] = v
        except Exception as e:
            print(f"Warning: could not read {config_path} ({e}). Using built-in defaults.")
    else:
        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            print(f"No config file found -- created a default one at {config_path}")
        except Exception as e:
            print(f"Warning: could not create default config at {config_path} ({e}).")

    config["addresses_file"] = _resolve_path(config["addresses_file"])
    config["output_directory"] = _resolve_path(config["output_directory"])

    return config
