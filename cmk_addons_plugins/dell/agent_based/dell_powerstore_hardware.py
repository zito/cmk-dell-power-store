#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell.powerstore_lib import (
    DellPowerStoreAPIData,
    parse_dell_powerstore,
)


agent_section_hardware = AgentSection(
    name="hardware",
    parse_function=parse_dell_powerstore,
    parsed_section_name="hardware",
)


def discovery_dell_powerstore_hardware(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:
    ids = []
    section.sort(key = lambda item: (item['type'], item['slot'], item['name']))
    for item in section:
        state = item.get("lifecycle_state")
        if state is not None and state != "Empty":
            ids.append(item["id"])
    if ids:
        yield Service(parameters={'ids':ids})
    else:
        return None


def check_dell_powerstore_hardware(
        params: list[str],
        section: DellPowerStoreAPIData
        ) -> CheckResult:
    info = []
    errs = []
    idmap = dict([(item.get("id"), item) for item in section])
    for id in params.get("ids", []):
        if id not in idmap:
            iteminfo = f"missing item id: {id}(!!)"
            errs.append(iteminfo)
        else:
            item = idmap[id]
            state = item.get("lifecycle_state")
            iteminfo = f"{item['name']}: {state}"
            if state != "Healthy":
                iteminfo += "(!!)"
                errs.append(iteminfo)
            iteminfo = f"Type: {item['type']}, Appliance: {item['appliance_id']}, " \
                    f"Slot: {item['slot']}, Name: {item['name']}, " \
                    f"Serial#: {item['serial_number']}, State: {state}"
        info.append(iteminfo)
    if errs:
        state = State.CRIT
        summary = f"There are #{len(errs)} problems in total, " + ", ".join(errs)
    else:
        state = State.OK
        summary = f"Everything is in the healthy state"
    details = "\n".join(info)
    yield Result(state=state, summary=summary, details=details)


check_plugin_dell_powerstore_hardware = CheckPlugin(
    name="dell_powerstore_hardware",
    service_name="Hardware",
    sections=["hardware"],
    discovery_function=discovery_dell_powerstore_hardware,
    check_function=check_dell_powerstore_hardware,
    check_default_parameters={},
)
