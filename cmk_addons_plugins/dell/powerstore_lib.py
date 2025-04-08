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
        section = json.loads("".join("".join(x) for x in string_table))
        return section
    except (IndexError, json.decoder.JSONDecodeError):
        return {}


def parse_dell_powerstore_hardware(string_table: StringTable) -> DellPowerStoreAPIData:
    section = parse_dell_powerstore(string_table)

    by_id = { x['id']: x for x in section }

    def _short_cut(d: dict) -> str:
        t = d['type']
        sc = t if len(t) <= 10 else ''.join(c for c in t if c.isupper() or c.isdigit())
        sc += f":{int(d['slot']):02d}"
        n = d['name']
        ns = n.split('-')
        if len(ns) > 1:
            scn = ns[-1]
            if scn[-1].isdigit() and not scn[-2].isdigit():
                scn = scn[0:-1] + ':0' + scn[-1]
            if len(scn) +2 <= len(sc):
                return scn
        return sc

    def _hw_path(d: dict) -> str:
        sc = _short_cut(d)
        return _hw_path(by_id[d['parent_id']]) + '/' + sc if d['parent_id'] else d['appliance_id']

    return { _hw_path(x): x for x in section }
