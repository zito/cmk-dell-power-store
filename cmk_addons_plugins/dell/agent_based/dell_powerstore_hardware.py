#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    render,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell.powerstore_lib import (
    DellPowerStoreAPIData,
    parse_dell_powerstore_hardware,
)
from pprint import pformat


agent_section_hardware = AgentSection(
    name="hardware",
    parse_function=parse_dell_powerstore_hardware,
    parsed_section_name="hardware",
)


def discovery_dell_powerstore_hardware(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:

    for hw_path, data in section.items():
        state = data.get("lifecycle_state")
        if state is not None and state != "Empty":
            yield Service(item=hw_path)
    else:
        return None


def check_dell_powerstore_hardware(
        item: str,
        params: list[str],
        section: DellPowerStoreAPIData
        ) -> CheckResult:

    if item not in section:
        yield Result(state=UNKNOWN, summary='data not found')
        return

    d = section[item]

    s = d.get("lifecycle_state")
    if s != "Healthy":
        yield Result(state=State.CRIT, summary=f"State: {s}(!!)")
    else:
        yield Result(state=State.OK, summary="State: Healthy")

    s = d.get("stale_state")
    if s != "Not_Stale":
        yield Result(state=State.WARN, summary=f"Stale State: {s}(!)")
    else:
        yield Result(state=State.OK, summary="Not Stale")

    de = d.get('extra_details', {})
    match d['type']:
        case 'Drive':
            dt = de.get('drive_type', 'unknown')
            dsz = render.bytes(de.get('size', 0))
            dfw = de.get('firmware_version', 'unknown')
            yield Result(state=State.OK, summary=f"{dt}, {dsz}, firmware: {dfw}")
        case 'Node':
            dcpu = de.get('cpu_model', 'unknown')
            dcore = de.get('cpu_cores', 'unknown')
            yield Result(state=State.OK, summary=f"CPU: {dcpu}, CPU Cores: {dcore}")
        case 'IO_Module':
            dmodel = de.get('model_name', 'unknown')
            yield Result(state=State.OK, summary=f"Model: {dmodel}")
        case 'SFP':
            dcon = de.get('connector_type', 'unknown')
            dmode = de.get('mode', 'unknown')
            dprot = de.get('supported_protocol', 'unknown')
            dspd = de.get('supported_speeds', 'unknown')
            yield Result(state=State.OK, summary=f"Connector: {dcon}, Mode: {dmode}, Proto: {dprot}, Speed: {dspd}")
    yield Result(state=State.OK, summary=f"Name: {d['name']}") #, details=pformat(d)



check_plugin_dell_powerstore_hardware = CheckPlugin(
    name="dell_powerstore_hardware",
    service_name="HW %s",
    sections=["hardware"],
    discovery_function=discovery_dell_powerstore_hardware,
    check_function=check_dell_powerstore_hardware,
    check_default_parameters={},
)
