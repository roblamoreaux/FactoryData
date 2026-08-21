import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import csv
import datetime
from encoder import *
import NVM_Data_S19_creator as nvm


def mac_plain_to_colon(hexstr):
    """Turn '0C73EBAA0000' into '0C:73:EB:AA:00:00'."""
    hexstr = hexstr.strip().upper()
    return ":".join(hexstr[i:i + 2] for i in range(0, len(hexstr), 2))


def mac_colon_to_plain(macstr):
    """Turn '0C:73:EB:AA:00:00' into '0C73EBAA0000'."""
    return macstr.replace(":", "").replace("-", "").strip().upper()

def decode_uint48(indat):
    hexstr =  "{0:012X}".format(indat)
    print("uint48={0}".format(hexstr))#hexstr):
    return str(int(hexstr, 16))

def decode_uint16(indat):
    hexstr =  "{0:012X}".format(indat)
    print("uint16={0}".format(hexstr))#hexstr):
    return str(int(hexstr, 16))

def decode_uint8(indat):
    hexstr =  "{0:012X}".format(indat)
    print("uint8={0}".format(hexstr))#hexstr):
    return str(int(hexstr, 16))

def decode_partnumber(indat):
    hexstr =  "{0:012X}".format(indat)
    print("ascii={0}".format(hexstr))#hexstr):
    b = bytes.fromhex(hexstr)
    pre = b[0]
    t0 = b[1]
    t = chr(t0)
    num = (b[2] << 24)| (b[3] << 16)| (b[4] << 8)| (b[5] << 0)
    return f"{pre:02d}{t}{num:06d}"

def decode_ascii(indat):
    hexstr =  "{0:012X}".format(indat)
    print("ascii={0}".format(hexstr))#hexstr):
    return bytes.fromhex(hexstr).decode("ascii").strip("\x00")

def decode_date_ssddmmyyyy_binary(indat):
    hexstr =  "{0:012X}".format(indat)
    print("datecode={0}".format(hexstr))
    b = bytes.fromhex(hexstr)
    shift = b[1]
    day = b[2]
    month = b[3]
    year = b[5] | (b[4] << 8)
    return shift, f"{year:04d}-{month:02d}-{day:02d}"

def decode_mac(indat):
    hexstr =  "{0:012X}".format(indat)
    print("datecode={0}".format(hexstr))
    b = bytes.fromhex(hexstr)
    rstr = f"{b[0]:02X}:{b[1]:02X}:{b[2]:02X}:{b[3]:02X}:{b[4]:02X}:{b[5]:02X}"
    print(f"MAC Addr: {rstr}")
    return rstr
def decode_issmod(indat):
    hexstr =  "{0:012X}".format(indat)
    print("datecode={0}".format(hexstr))
    b = bytes.fromhex(hexstr)
    rstr = f"{b[4]:02X}:{b[5]:02X}"
    print(f"MAC Addr: {rstr}")
    return rstr

class App:
    def __init__(self, root, schema, factory_dict, build_factory_data, config):
        self.root = root
        self.schema = schema
        self.factory_dict = factory_dict
        self.build_factory_data = build_factory_data
        self.config = config
        self.addresses_path = config["addresses_file"]
        self.output_directory = config["output_directory"]
        self.entries = {}
        r = 0
        tk.Label(root, text='Shift').grid(row=r,column=0)
        self.shift = tk.Entry(root); self.shift.grid(row=r,column=1); r+=1
        """ 
        for k in schema['fields']:
            tk.Label(root, text=k).grid(row=r,column=0)
            e = tk.Entry(root); e.grid(row=r,column=1)
            self.entries[k]=e; r+=1
        """
        defaults = getattr(nvm, "DEFAULT_FACTORY_DATA", {})

        for name, field in schema["fields"].items():
            tk.Label(root, text=name).grid(row=r, column=0, sticky="w")
            e = tk.Entry(root, width=30)

            key = int(field["hex_key"], 16)
            #hexval = defaults.get(key)
            hexval = factory_dict.get(key)
            # Decode based on type
            if hexval:
                t = field["type"]

                if t == "uint48":
                    e.insert(0, decode_uint48(hexval))

                if t == "uint8":
                    e.insert(0, decode_uint8(hexval))

                if t == "uint16":
                    e.insert(0, decode_uint16(hexval))

                elif t == "ascii":
                    e.insert(0, decode_ascii(hexval))

                elif t == "partnum":
                    e.insert(0, decode_partnumber(hexval))
                elif t == "issmod":
                    e.insert(0, decode_issmod(hexval))
                elif t == "mac":
                    e.insert(0, decode_mac(hexval))

                elif t == "date_ssddmmyyyy_binary":
                    shift, datestr = decode_date_ssddmmyyyy_binary(hexval)
                    self.shift.insert(0, str(shift))
                    e.insert(0, datestr)

            e.grid(row=r, column=1)
            self.entries[name] = e
            r += 1

        tk.Button(root, text='Submit', command=self.submit).grid(row=r, column=0)
        tk.Button(root, text='Exit', command=self.exit_app).grid(row=r, column=1)

        # Load Addresses.txt and pre-fill the MAC fields from the first
        # row that doesn't yet have a serial number assigned.
        self.address_header = None
        self.address_rows = []
        self.current_row_index = None
        self.load_next_available_addresses()

    # ------------------------------------------------------------------
    # Addresses.txt handling
    # ------------------------------------------------------------------
    def read_addresses(self):
        """Read Addresses.txt into self.address_header / self.address_rows."""
        with open(self.addresses_path, newline='') as f:
            rows = list(csv.reader(f))
        if not rows:
            raise ValueError(f"{self.addresses_path} is empty.")
        self.address_header = rows[0]
        self.address_rows = rows[1:]
        self.ensure_extended_header()

    def extra_field_columns(self):
        """
        Names of the extra columns we track in Addresses.txt for every
        schema field except serialNumber/PLC_MAC_address/Enet_MAC_Address,
        which already have their own dedicated columns (Serial Number,
        PLC, Ethernet). "Shift" is included too since it's a distinct
        value entered in the form even though it isn't a schema field.
        "Timestamp" records when the S19 file for that row was created.
        """
        return ["Shift"] + [
            name for name in self.schema["fields"]
            if name not in ("serialNumber", "PLC_MAC_address", "Enet_MAC_Address")
        ] + ["Timestamp"]

    def ensure_extended_header(self):
        """
        Make sure self.address_header has a column for every extra factory
        field, adding any that are missing (this upgrades older
        Addresses.txt files in place) and padding existing rows so they
        stay aligned with the new, longer header.
        """
        added_any = False
        for col in self.extra_field_columns():
            if col not in self.address_header:
                self.address_header.append(col)
                added_any = True

        if added_any:
            target_len = len(self.address_header)
            for row in self.address_rows:
                while len(row) < target_len:
                    row.append("")

    def write_addresses(self):
        """Write self.address_header / self.address_rows back to Addresses.txt."""
        tmp_path = self.addresses_path + ".tmp"
        with open(tmp_path, "w", newline='') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(self.address_header)
            writer.writerows(self.address_rows)
        os.replace(tmp_path, self.addresses_path)

    def find_row_by_serial(self, serial):
        """Return the row index whose Serial Number column matches `serial`, or None."""
        for i, row in enumerate(self.address_rows):
            if len(row) > 1 and row[1].strip() == serial:
                return i
        return None

    def find_next_blank_row(self, start=0):
        """Return the index of the next row (from `start`) with a blank Serial Number."""
        for i in range(start, len(self.address_rows)):
            row = self.address_rows[i]
            if len(row) > 1 and row[1].strip() == "":
                return i
        return None

    def fill_mac_fields_from_row(self, idx):
        """Populate the PLC/Enet MAC entries from address_rows[idx]."""
        row = self.address_rows[idx]
        plc_mac = row[0].strip() if len(row) > 0 else ""
        enet_mac = row[2].strip() if len(row) > 2 else ""

        self.entries["PLC_MAC_address"].delete(0, tk.END)
        self.entries["PLC_MAC_address"].insert(0, mac_plain_to_colon(plc_mac))

        self.entries["Enet_MAC_Address"].delete(0, tk.END)
        self.entries["Enet_MAC_Address"].insert(0, mac_plain_to_colon(enet_mac))

        self.current_row_index = idx

    def load_next_available_addresses(self):
        """Read Addresses.txt fresh and fill in the next unused MAC pair."""
        try:
            self.read_addresses()
        except FileNotFoundError:
            messagebox.showerror(
                "Addresses.txt not found",
                f"Could not find {self.addresses_path}."
            )
            self.current_row_index = None
            return
        except Exception as e:
            messagebox.showerror("Error reading Addresses.txt", str(e))
            self.current_row_index = None
            return

        idx = self.find_next_blank_row(0)
        if idx is None:
            messagebox.showwarning(
                "No addresses available",
                "There are no more unused MAC address entries left in Addresses.txt."
            )
            self.current_row_index = None
            return

        self.fill_mac_fields_from_row(idx)

    def submit(self):
        """
        Build the factory data from the current GUI entries and create
        the S19 file. Does NOT close the window -- the user stays in the
        GUI and can submit again or press Exit when done.
        """
        try:
            shift_value = int(self.shift.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Shift must be an integer.")
            return

        serial = self.entries["serialNumber"].get().strip()
        if not serial:
            messagebox.showerror("Invalid input", "Serial Number is required.")
            return

        # Re-read Addresses.txt so we're checking against the latest data on disk.
        try:
            self.read_addresses()
        except FileNotFoundError:
            messagebox.showerror(
                "Addresses.txt not found",
                f"Could not find {self.addresses_path}."
            )
            return
        except Exception as e:
            messagebox.showerror("Error reading Addresses.txt", str(e))
            return

        # 1) Verify the serial number isn't already used.
        existing_idx = self.find_row_by_serial(serial)
        if existing_idx is not None:
            existing_row = self.address_rows[existing_idx]
            messagebox.showerror(
                "Duplicate Serial Number",
                f"Serial Number '{serial}' already exists in Addresses.txt "
                f"(PLC MAC {existing_row[0]})."
            )
            return

        # 2) Find the row matching the MAC addresses currently shown in the form.
        plc_mac_plain = mac_colon_to_plain(self.entries["PLC_MAC_address"].get())
        row_idx = None
        for i, row in enumerate(self.address_rows):
            if len(row) > 0 and row[0].strip().upper() == plc_mac_plain:
                row_idx = i
                break

        if row_idx is None:
            messagebox.showerror(
                "MAC address not found",
                "Could not find the currently displayed PLC MAC address in "
                "Addresses.txt. Please reload and try again."
            )
            return

        if self.address_rows[row_idx][1].strip() != "":
            messagebox.showerror(
                "MAC address already assigned",
                "The displayed MAC address row already has a Serial Number "
                "assigned. Please reload to get a fresh, unused address."
            )
            return

        # 3) Create the S19 file FIRST. Addresses.txt is only written to
        #    once this succeeds, so a failure here leaves Addresses.txt
        #    completely untouched -- no rollback needed.
        class Args:
            pass

        args = Args()
        args.shift = shift_value
        for name in self.schema["fields"]:
            setattr(args, name, self.entries[name].get())

        try:
            factory_dict = self.build_factory_data(self.schema, args)

            os.makedirs(self.output_directory, exist_ok=True)
            s19_basename = os.path.join(self.output_directory, serial + "-")
            s19_file = nvm.new_s19_creator(s19_basename)

            new_data_line_count = nvm.change_s19(factory_dict, s19_file)
            nvm.add_buffer_lines(new_data_line_count, 'platform-registry.s19', s19_file)
        except Exception as e:
            messagebox.showerror("Error creating S19", str(e))
            return

        # 4) Only now write the serial number and all other field values
        #    into Addresses.txt and save.
        row = self.address_rows[row_idx]
        while len(row) < len(self.address_header):
            row.append("")

        row[1] = serial

        shift_col = self.address_header.index("Shift")
        row[shift_col] = str(shift_value)

        for name in self.schema["fields"]:
            if name in ("serialNumber", "PLC_MAC_address", "Enet_MAC_Address"):
                continue
            col_idx = self.address_header.index(name)
            row[col_idx] = self.entries[name].get()

        timestamp_col = self.address_header.index("Timestamp")
        row[timestamp_col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            self.write_addresses()
        except Exception as e:
            messagebox.showerror(
                "S19 created, but Addresses.txt failed to save",
                f"S19 file '{s19_file}' was created successfully, but "
                f"Addresses.txt could not be updated: {e}\n\n"
                f"Please manually record Serial Number '{serial}' against "
                f"PLC MAC {self.address_rows[row_idx][0]} in Addresses.txt."
            )
            return

        messagebox.showinfo("Success", f"S19 created and updated: {s19_file}")

        # 5) Advance the MAC fields to the next unused row for the next unit.
        self.entries["serialNumber"].delete(0, tk.END)
        self.load_next_available_addresses()

    def exit_app(self):
        """The only action that actually closes the GUI/program."""
        self.root.destroy()

def run_gui(schema, factory_dict, build_factory_data, config):
    root = tk.Tk()
    root.title("NVM S19 Factory Tool")
    app = App(root, schema, factory_dict, build_factory_data, config)
    root.mainloop()
    return app