import argparse
import json
import NVM_Data_S19_creator as nvm
from encoder import *
from gui import run_gui
from config import load_config


def load_defaults():
    """
    Load default factory data from NVM_Data_S19_creator if defined
    """
    return getattr(nvm, "DEFAULT_FACTORY_DATA", {}).copy()

def build_factory_data(schema, args):
    factory_data = load_defaults()

    for name, field in schema["fields"].items():
        print("***Default-Name={0}:key={1}:type= {2}:value={3}".format(name,field["hex_key"],field["type"],factory_data[int(field["hex_key"], 16)]))
        value = getattr(args, name, None)
        if not value:
            print("No Value")
            #value = 0
            continue

        key = int(field["hex_key"], 16)
        t = field["type"]
        print("***Key={0}:type= {1}:value={2}".format(key,t,value))
        
        if t == "uint48":
            factory_data[key] = encode_uint48(value)

        elif t == "date_ssddmmyyyy_binary":
            factory_data[key] = encode_date_ssddmmyyyy_binary(
                value, 1 #args.shift
            )

        elif t == "ascii":
            factory_data[key] = encode_ascii(value)
            print("***Key={0:04X}:factorydata={1}:value={2}".format(key,factory_data[key],value))
        elif t == "partnum":
            factory_data[key] = encode_partnumber(value)
            print("***Key={0:04X}:factorydata={1:08X}:value={2}".format(key,factory_data[key],value))
        elif t == "uint8":
            factory_data[key] = encode_uint8(value)
            print("***Key={0:04X}:factorydata={1:08X}:value={2}".format(key,factory_data[key],value))
        elif t == "uint16":
            factory_data[key] = encode_uint16(value)
            print("***Key={0:04X}:factorydata={1:08X}:value={2}".format(key,factory_data[key],value))
        elif t == "issmod":
            factory_data[key] = encode_issmod(value)
            print("**ismKey={0:04X}:factorydata={1:08X}:value={2}".format(key,factory_data[key],value))
        elif t == "mac":
            print(f"mac value={value}")
            factory_data[key] = encode_mac(value)
            print("***Key={0:04X}:factorydata={1:0}:value={2}".format(key,factory_data[key],value))
    return factory_data

if __name__ == "__main__":
    config = load_config()
    initial_values = config.get("initial_values", {})

    parser = argparse.ArgumentParser("NVM S19 Factory Tool")
    parser.add_argument("--shift", type=int, default=initial_values.get("shift"))

    # auto-generated CLI args
    with open("factory_schema.json") as f:
        schema = json.load(f)

    for k in schema["fields"]:
        parser.add_argument(f"--{k}", default=initial_values.get(k))

    args = parser.parse_args()

    # Build initial factory data (config initial values + any CLI overrides) to pre-fill the GUI
    factory_dict = build_factory_data(schema, args)

    # Always enter the GUI. Each "Submit" click inside the GUI builds and
    # writes an S19 file without closing the window; the program only exits
    # once the user presses the "Exit" button in the GUI.
    print("Starting gui")
    run_gui(schema, factory_dict, build_factory_data, config)

    print("GUI closed. Exiting program.")