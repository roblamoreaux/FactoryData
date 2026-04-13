from datetime import datetime

def encode_uint48(value):
    if not value.isdigit(): raise ValueError('Serial must be numeric')
    n = int(value)
    if n > 0xFFFFFFFFFFFF: raise ValueError('Out of range')
    print("n={0:08X}".format(n))
    s = "{0:08X}".format(n)
    return  int(s, 16) & 0xFFFFFFFFFFFF #n.to_bytes(6, 'big').hex().upper()


def encode_partnumber(v):
    pre = int(v[0:2])
    char_var = ord(v[2])
    print(f"{char_var}")
    pnum = int(v[3:])
    print (f" 1: {pre}, C: {char_var},  2: {pnum} hex {(pre <<40) | (char_var<< 32) | (pnum):012X}")
    return (pre <<40) | (char_var<< 32) | (pnum)

def encode_date_ssddmmyyyy_binary(date_str, shift):
    d = datetime.strptime(date_str, '%Y-%m-%d')
    y = d.year
    dat = (
        f"{00 & 0xFF:02X}"
        f"{shift & 0xFF:02X}"
        f"{d.day & 0xFF:02X}"
        f"{d.month & 0xFF:02X}"
        f"{(y >> 8) & 0xFF:02X}"
        f"{y & 0xFF:02X}"
            )
    print("dat={0}".format(dat))
    return int(dat, 16) & 0xFFFFFFFFFFFF
   

def encode_ascii(v): 
    t = int(v.encode('ascii').hex().upper(),16)
    print(f"encode ascii {v}: {t}")
    return t

def encode_uint8(v): 
    print (int(f"{int(v)&0xFF:02X}",16))
    return int(f"{int(v)&0xFF:02X}",16)

def encode_uint16(v): return int(f"{int(v)&0xFFFF:04X}",16)

def encode_issmod(v): 
    print(f"issue and mod:{str(v.replace(':','').replace('-','').upper())}")
    print(f"0x{v.replace(':','').replace('-','').upper()}")
    print(int(f"0x{v.replace(':','').replace('-','').upper()}",16))
    #return int(f"0x{int(v.replace(':','').replace('-','').upper())&0xFFFF:04X}",16)
    return (int(f"0x{v.replace(':','').replace('-','').upper()}",16))
def encode_mac(v): return int(v.replace(':','').replace('-','').upper(),16)
