# NVM S19 Factory Tool – Full Integration

This project provides:
- Full schema-driven key support
- Binary encoders for all fields
- CLI + GUI front end
- CI-friendly non-interactive mode
- Direct integration hook for change_s19()

## Usage (CI / CLI)
usage: NVM S19 Factory Tool [-h] [--gui] [--shift SHIFT] [--dateMGF DATEMGF] [--Base_PN BASE_PN] [--issue_mod ISSUE_MOD] [--serialNumber SERIALNUMBER]
                            [--mfg_Location MFG_LOCATION] [--developer_features DEVELOPER_FEATURES] [--PLC_MAC_address PLC_MAC_ADDRESS] [--PIB_PN PIB_PN]
                            [--Enet_MAC_Address ENET_MAC_ADDRESS] [--base_PN_at_MFG BASE_PN_AT_MFG] [--Config_Issue_at_MFG CONFIG_ISSUE_AT_MFG]
                            [--HW_product_name_Part1 HW_PRODUCT_NAME_PART1] [--HW_product_name_Part2 HW_PRODUCT_NAME_PART2]

options:
  -h, --help            show this help message and exit
  --gui
  --shift SHIFT
  --dateMGF DATEMGF
  --Base_PN BASE_PN
  --issue_mod ISSUE_MOD
  --serialNumber SERIALNUMBER
  --mfg_Location MFG_LOCATION
  --developer_features DEVELOPER_FEATURES
  --PLC_MAC_address PLC_MAC_ADDRESS
  --PIB_PN PIB_PN
  --Enet_MAC_Address ENET_MAC_ADDRESS
  --base_PN_at_MFG BASE_PN_AT_MFG
  --Config_Issue_at_MFG CONFIG_ISSUE_AT_MFG
  --HW_product_name_Part1 HW_PRODUCT_NAME_PART1
  --HW_product_name_Part2 HW_PRODUCT_NAME_PART2

```bash
python create-srec.py --shift=02 --serialNumber=325041100998  --dateMGF=2026-04-01 --Base_PN=01T0700181 --issue_mod=03:00 --gui
```

## GUI
```bash
python main.py --gui
```
