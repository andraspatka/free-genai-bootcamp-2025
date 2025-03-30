#!/usr/bin/env python
"""
Debug entry point that enables remote debugging with debugpy.
Run this script instead of main.py when you want to debug.
"""

import debugpy
import time
import os
import sys

# Enable debugger
debugpy.listen(("0.0.0.0", 5678))
print("⏳ Waiting for debugger to attach at 0.0.0.0:5678...")
debugpy.wait_for_client()
print("🔍 Debugger attached! Starting application...")

# Import and run the actual application
import main

if __name__ == "__main__":
    main.main()
