import argparse
from pathlib import Path
import binascii
import crcmod
import shutil
import time

# ## Future updates - Making a command line tool.
# ## Add arguements to send all factory data at once.
# parser = argparse.ArgumentParser(prog='NVM_Data_Update',
#                                  description='Updates NVM data of a s19 record and produces a new s19 '
#                                              'User must add Serial Number')

# parser.add_argument('serial', metavar='<SerialNumber>',
#                     help='Pass in Serial Number for the unit')

# args = parser.parse_args()

def write_32(a, addr, v):
    if a is None: a = [0, 0, 0, 0]
    write_16(a, addr + 0, v >>  0)
    write_16(a, addr + 2, v >> 16)
    return a

def write_16(a, addr, v):
    if a is None: a = [0, 0]
    write_8(a, addr + 0, v >> 0)
    write_8(a, addr + 1, v >> 8)
    return a

def write_8(a, addr, v):
    if a is None: a = [0]
    a[addr] = v & 0xFF
    return a

def read_32(a, addr):
    rc = (read_16(a, addr + 2) << 16) | (read_16(a, addr + 0) << 0)
    return rc & 0xFFFFFFFF

def read_16(a, addr):
    rc = (read_8(a, addr + 1) << 8) | (read_8(a, addr + 0) << 0)
    return rc & 0xFFFF

def read_8(a, addr):
    return a[addr] & 0xFF

def gen_s3_line(addr, rep):
    """ Adjust address according to memory configuration and generate an s-rec line"""

    c = len(rep) + 5
    for b in write_32(None, 0, addr):
        c += b
    for i in range(len(rep)):
        c += rep[i]

    # return a tuple of addr, s3 line
    return addr, "S3%02X%08X%s%02X\n" % (len(rep) + 5,
                                         addr,
                                         binascii.hexlify(rep).upper().decode('utf-8'),
                                         255 - (c % 256))

def Calc_Crc(hex_string):
    """ Calculates CRC-16 (CCITT-FALSE) for the bytearray given to this function. """
    crc32_func = crcmod.predefined.mkCrcFun('crc-ccitt-false')
    crc = crc32_func(bytes.fromhex(hex_string))
    return crc

def new_s19_creator():
    """ Creates an new s19 with time stamp."""

    timestr = time.strftime("%Y-%m_%d_%H_%M_%S")

    new_s19 = timestr + '_' + "platform-registry.s19"

    # Create a new file
    file = Path(new_s19)

    if not file.exists():
        file.write_text("This file is created using pathlib!")
    else:
        print("File already exists!")

    return new_s19
        

def change_s19(dict_key_factory_data, s19):
    """ Changes the new s19 file to add required inital data, checksum, new key + data, etc.
        Provide a dictonary of keys and data as argument 1 and a blank s19 name string in arguement 2."""

    start_of_s19 = "BE6151B10101"
        
    _always_zeros = "00000000"

    counter = 0x0

    modified_key_plus_data = ''

    for key, values in dict_key_factory_data.items():
        key_plus_data = "{:04X}".format(key) + "{:012X}".format(values)
        print("keyplusdata: " + key_plus_data)
        modified_key_plus_data += key_plus_data
        counter += 1
    print("counter = {0}".format(counter))
    checksum = Calc_Crc("{:08X}".format(counter) + _always_zeros + modified_key_plus_data)
    print("Checksum = {:04X}".format(checksum))
    all_data = bytes.fromhex(start_of_s19 + format(checksum, '04X') + format(counter, '08X') + _always_zeros + modified_key_plus_data)

    line = []

    line_length = 32

    cntr = 0
    
    for j in range(0, len(bytearray(all_data)), line_length):
        cntr += 1
        split_data = all_data[j:j+line_length]
        if len(split_data) < line_length:
            line_buffer = bytearray(line_length - len(split_data))
            split_data = split_data + line_buffer
        _addr, new_line = gen_s3_line(0x80100000 + j, split_data)
        line.append(new_line)

    with open(s19, 'w') as fp:
        fp.writelines(line)
        print("Write Successful")

    return cntr

def add_buffer_lines(new_lines, s19_with_buffers, s19_without_buffers):
    """ Add buffers to the new s19 using a working s19 file."""

    with open(s19_with_buffers, 'r') as fp:

        lines = fp.readlines()

    for item in range(new_lines):
        lines.pop(0)          

    with open(s19_without_buffers, 'a') as fp:
        fp.writelines(lines)
        print("Buffer added")


if __name__ == "__main__":

    temp_s19 = new_s19_creator()
    new_data_line_count = change_s19({0x01:0x000000000000,  # Key 1
				                      0x02:0x0001010407EA,	# date of manufacture (00 SH DD MM YYYY)
				                      0x03:0x01540001130C, 	# Base PN (01 T 070412)
                                      0x04:0x000000000300, 	# issue and mod (000 03 00)
                                      0x05:0x000000000000, 	# Key 5
                                      0x06:0x000000000000, 	# key 6
                                      0x07:0x000000000000, 	# key 7
                                      0x08:0x004BADF59545, 	# serial number              
                                      0x09:0x000000000000, 	# key 9
                                      0x0A:0x202020555349, 	# mfg name (   USI)
                                      0x0B:0x000000000000, 	# developer features
                                      0x10:0x0C73EBAA0061, 	# PLC MAC address
                                      0x12:0x0C73EBAB0061, 	# Ethernet MAC Address
 				                      0x11:0x002000000000, 	# PIB PN (0 000000)
                                      0x80:0x025400011309,  # base Pn at MFG ( 02 T 070409)
                                      0x81:0x000000000001, 	# Config Issue PN at MFG (00 00 00 00 00 01)
                                      0x82:0x4E78332D3030, 	# HW product name (Nx3-00)	
                                      0x83:0x302020202020}, # HW product name part 2 (0     )		
					   temp_s19)
    
    add_buffer_lines(new_data_line_count, 'platform-registry.s19', temp_s19)

