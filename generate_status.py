#!/usr/bin/env python3
import json
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('status', choices=['running', 'completed'])
parser.add_argument('--output', default='generator_status.json')
args = parser.parse_args()

payload = {
    'status': args.status,
    'timestamp': int(time.time()),
}

with open(args.output, 'w') as f:
    json.dump(payload, f, indent=2)

print(f"Wrote {args.status} status to {args.output}")
