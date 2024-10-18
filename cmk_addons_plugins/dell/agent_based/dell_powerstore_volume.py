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
from cmk.plugins.lib.df import (
    check_filesystem_levels,
    FILESYSTEM_DEFAULT_LEVELS,
    MAGIC_FACTOR_DEFAULT_PARAMS,
)
from cmk_addons.plugins.dell.powerstore_lib import (
    DellPowerStoreAPIData,
    parse_dell_powerstore,
)


agent_section_volume = AgentSection(
    name="volume",
    parse_function=parse_dell_powerstore,
    parsed_section_name="volume",
)


def discovery_dell_powerstore_volume(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:
    for d in section:
        if d["type"] == "Primary":
            item = d["appliance_id"] + " " + d["name"]
            yield Service(item=item, parameters={'id':d["id"]})


def check_dell_powerstore_volume(
        item: str,
        params: list[str],
        section: DellPowerStoreAPIData
        ) -> CheckResult:
    for d in section:
        if d["id"] == params["id"]:
            break
    else:
        yield Result(state=State.UNKNOWN, summary=f"volume id {params['id']} not found")

    used = d["logical_used"]
    size = d["size"]
    free = size - used
    used_mb = used / 1024**2
    size_mb = size / 1024**2
    free_mb = free / 1024**2

    yield Result(state=State.OK if d["state"] == "Ready" else State.WARN,
                    summary=f"State: {d['state']}")
    yield from check_filesystem_levels(size_mb, size_mb, free_mb, used_mb,
                    params)


check_plugin_dell_powerstore_volume = CheckPlugin(
    name="dell_powerstore_volume",
    service_name="Volume %s",
    sections=["volume"],
    discovery_function=discovery_dell_powerstore_volume,
    check_function=check_dell_powerstore_volume,
    check_ruleset_name="filesystem",
    check_default_parameters={
        **FILESYSTEM_DEFAULT_LEVELS,
        **MAGIC_FACTOR_DEFAULT_PARAMS,
    },
)
