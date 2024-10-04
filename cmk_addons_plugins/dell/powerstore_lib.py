#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""functions for all dell_powerstore components"""

# License: GNU General Public License v2

import json
from typing import Any, Dict, NamedTuple, Optional, Tuple
from cmk.agent_based.v2 import AgentSection, DiscoveryResult, Service, StringTable


DellPowerStoreAPIData = Dict[str, object]


def parse_dell_powerstore(string_table: StringTable) -> DellPowerStoreAPIData:
    """parse one line of data to dictionary"""
    try:
        return json.loads("".join("".join(x) for x in string_table))
    except (IndexError, json.decoder.JSONDecodeError):
        return {}

