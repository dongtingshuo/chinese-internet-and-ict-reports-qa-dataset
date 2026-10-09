#!/usr/bin/env python3
"""Compatibility entry point for the active v2.1.0 package validator."""
from validate_v2_1_package import validate

if __name__ == "__main__":
    import json
    import sys

    issues, stats = validate()
    print(json.dumps({"issues": issues, "stats": stats}, ensure_ascii=False, indent=2))
    sys.exit(1 if issues else 0)
