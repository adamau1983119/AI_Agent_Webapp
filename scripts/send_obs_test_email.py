#!/usr/bin/env python3
"""已廢止假測試信。請改用：python scripts/run_obs_ops_agent_once.py"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

print("WARN | send_obs_test_email 已廢止；改跑 Ops Agent 真實告警")
target = Path(__file__).with_name("run_obs_ops_agent_once.py")
sys.argv = [str(target)]
runpy.run_path(str(target), run_name="__main__")
