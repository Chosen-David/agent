"""Independent invocation of inspected measurement, preserving producer outputs."""
import importlib.util
import json
from pathlib import Path
import sys
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('independently_invoked_native_measurement', OUT / 'measure_native.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.measure()
label = '-' + sys.argv[1] if len(sys.argv) > 1 else ''
name = 'independent-raw-native-v3' + label + '.json'
with (OUT / name).open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'scenarios': len(result['observations']), 'output': name}))
