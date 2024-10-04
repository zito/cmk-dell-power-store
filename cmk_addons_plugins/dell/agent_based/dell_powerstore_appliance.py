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


agent_section_appliance = AgentSection(
    name="appliance",
    parse_function=parse_dell_powerstore,
    parsed_section_name="appliance",
)


def discovery_dell_powerstore_appliance(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:
    for item in section:
        if 'id' in item:
            yield Service(item=item["id"])


def check_dell_powerstore_appliance(
        item, section: DellPowerStoreAPIData
        ) -> CheckResult:
    info = []
    errs = []
    idmap = dict([(item.get("id"), item) for item in section])
    if item in idmap:
        d = idmap[item]
        yield Result(state=State.OK, summary=f"Name: {d.get('name')}, " \
                f"Model: {d.get('model', 'unknown')}, " \
                f"Node Count: {d.get('node_count', 'unknown')}, " \
                f"Service Tag: {d.get('service_tag', 'unknown')}")
    else:
        yield Result(state=State.UKWN, summary="Item not found(!!)")


check_plugin_dell_powerstore_appliance = CheckPlugin(
    name="dell_powerstore_appliance",
    service_name="Appliance %s",
    sections=["appliance"],
    discovery_function=discovery_dell_powerstore_appliance,
    check_function=check_dell_powerstore_appliance,
)
