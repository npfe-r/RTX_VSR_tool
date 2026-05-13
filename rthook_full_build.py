"""Runtime hook for the Full build — marks the build as full so app.py
skips the startup dependency scan (all deps are already bundled)."""
import os
os.environ["RTX_BUILD"] = "full"
