#!/usr/bin/env python3
"""
Quick test to verify FastAPI app can start with Phase 2 components
"""
import sys
import os
import asyncio

# Change to backend directory
os.chdir(os.path.dirname(__file__))

try:
    # Import the main app
    from main import app
    print("✓ FastAPI app imported successfully")
    
    # Count routers
    routers = [route for route in app.routes if hasattr(route, 'tags')]
    print(f"✓ {len(app.routes)} routes registered")
    print(f"✓ FastAPI app is ready to start")
    
     # List all endpoints
    endpoints = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            endpoints.append(f"  {', '.join(route.methods)} {route.path}")
    
    if endpoints:
        print("✓ Endpoints registered:")
        for ep in endpoints[:10]:  # Show first 10
            print(ep)
        if len(endpoints) > 10:
            print(f"  ... and {len(endpoints) - 10} more")
    
    sys.exit(0)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
