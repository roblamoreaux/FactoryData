# NVM S19 Factory Tool – Full Integration

This project provides:
- Full schema-driven key support
- Binary encoders for all fields
- CLI + GUI front end
- CI-friendly non-interactive mode
- Direct integration hook for change_s19()

## Usage (CI / CLI)
```bash
python main.py   --input-s19 base.s19   --output-s19 out.s19   --shift 3   --serialNumber 123456789   --dateMGF 2026-04-10
```

## GUI
```bash
python main.py --gui
```
