import argparse
import json
import NVM_Data_S19_creator as nvm
from encoder import *
from gui import run_gui


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
                value, args.shift
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
    parser = argparse.ArgumentParser("NVM S19 Factory Tool")
    parser.add_argument("--gui", action="store_true")
    parser.add_argument("--shift", type=int, required=True)

    # auto-generated CLI args
    with open("factory_schema.json") as f:
        schema = json.load(f)

    for k in schema["fields"]:
        parser.add_argument(f"--{k}")

    args = parser.parse_args()
    if args.gui:
        print("Starting gui")
        app = run_gui(schema)

        # Pull values from GUI into args
        args.shift = int(app.shift.get())

        for name in schema["fields"]:
            setattr(args, name, app.entries[name].get())
#

    # 1️⃣ Create new S19 via enclosed module
    s19_file = nvm.new_s19_creator()

    # 2️⃣ Build factory data (defaults + user overrides)
    factory_dict = build_factory_data(schema, args)

    # 3️⃣ Apply factory data using enclosed function
    new_data_line_count = nvm.change_s19(factory_dict, s19_file)
    nvm.add_buffer_lines(new_data_line_count, 'platform-registry.s19', s19_file)

    print(f"✅ S19 created and updated: {s19_file}")