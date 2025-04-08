#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    render,
    Result,
    Service,
    State,
)
from cmk_addons.plugins.dell.powerstore_lib import (
    DellPowerStoreAPIData,
    parse_dell_powerstore,
)
import datetime


agent_section_performance_metrics_by_appliance = AgentSection(
    name="performance_metrics_by_appliance",
    parse_function=parse_dell_powerstore,
    parsed_section_name="performance_metrics_by_appliance",
)


def discovery_dell_powerstore_performance(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:
    for item in section:
        if 'appliance_id' in item:
            yield Service(item=item["appliance_id"])


def check_dell_powerstore_performance(
        item, section: DellPowerStoreAPIData
        ) -> CheckResult:
    for d in section:
        if item == d["appliance_id"]:
#            dt = datetime.datetime.strptime(d["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
#            dt = dt.replace(tzinfo=datetime.timezone.utc)
#            dt = dt.astimezone()
            total_iops = float(d["total_iops"])
            total_bandwidth = float(d["total_bandwidth"])
            yield Metric(f"total_iops", total_iops)
            yield Metric(f"total_bandwidth", total_bandwidth)
            yield Result(state=State.OK, summary=f"Timestamp {dt}: "\
                    f"total_iops: {total_iops} IO/s, " \
                    f"total_bandwidth: {render.iobandwidth(total_bandwidth)}, " \
                    )
            return
    else:
        yield Result(state=State.UNKNOWN, summary="Item not found(!!)")


check_plugin_dell_powerstore_performance = CheckPlugin(
    name="dell_powerstore_performance",
    service_name="Performance %s",
    sections=["performance_metrics_by_appliance"],
    discovery_function=discovery_dell_powerstore_performance,
    check_function=check_dell_powerstore_performance,
)
