#!/usr/bin/env python3
"""OMK CLI — Operational Monitoring & Knowledge for Hermes Agent."""
import sys
import os

# Add the parent directory to path so imports work when run as module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from omk.cli import main

if __name__ == "__main__":
    main()
