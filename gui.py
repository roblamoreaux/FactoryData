import tkinter as tk
from tkinter import messagebox, filedialog
import json
from encoder import *
import NVM_Data_S19_creator as nvm

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
    def __init__(self, root, schema, factory_dict):
        self.root = root
        self.schema = schema
        self.factory_dict = factory_dict
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
        tk.Button(root,text='Submit',command=self.submit).grid(row=r,column=0,columnspan=2)
    def submit(self): self.root.quit()

def run_gui(schema, factory_dict):
    root=tk.Tk(); app=App(root,schema, factory_dict); root.mainloop(); return app
