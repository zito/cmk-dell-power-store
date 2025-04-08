#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# License: GNU General Public License v2

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    check_levels,
    DiscoveryResult,
    LevelsT,
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
from typing import Any, Generic, NotRequired, TypedDict, TypeVar
import datetime


agent_section_space_metrics_by_appliance = AgentSection(
    name="space_metrics_by_appliance",
    parse_function=parse_dell_powerstore,
    parsed_section_name="space_metrics_by_appliance",
)


def discovery_dell_powerstore_space(
        section: DellPowerStoreAPIData
        ) -> DiscoveryResult:
    for item in section:
        if 'appliance_id' in item:
            yield Service(item=item["appliance_id"])


_NumberT = TypeVar("_NumberT", int, float)

class _DualLevels(TypedDict, Generic[_NumberT]):
    lower: LevelsT[_NumberT]
    upper: LevelsT[_NumberT]

class _Levels(TypedDict):
    perc_used: NotRequired[_DualLevels[float]]

class Params(TypedDict):
    capacity: _Levels

_NO_LEVELS = _DualLevels(lower=("no_levels", None), upper=("no_levels", None))


def check_dell_powerstore_space(
        item,  params: Params, section: DellPowerStoreAPIData
        ) -> CheckResult:
    for d in section:
        if item == d["appliance_id"]:
#            dt = datetime.datetime.strptime(d["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
#            dt = dt.replace(tzinfo=datetime.timezone.utc)
#            dt = dt.astimezone()
            physical_total = int(d['physical_total'])
            physical_used = int(d['physical_used'])
            physical_free = physical_total - physical_used
            levels = params["capacity"]
            perc_used = levels.get("perc_used", _NO_LEVELS)
            data_reduction = float(d['data_reduction'])
            yield Metric("physical_free", physical_free)
            yield Metric("physical_used", physical_used)
            yield Metric("data_reduction", data_reduction)
            yield Result(state=State.OK, summary=f"Data reduction ratio: {data_reduction:0.2f}")
            yield from check_levels(
                    physical_used / physical_total * 100.0,
                    label=f"Used space",
                    levels_lower=perc_used["lower"],
                    levels_upper=perc_used["upper"],
                    render_func=render.percent,
                    metric_name=f"physical_used_percent",
                )
            return
    else:
        yield Result(state=State.UNKNOWN, summary="Item not found(!!)")


check_plugin_dell_powerstore_space = CheckPlugin(
    name="dell_powerstore_space",
    service_name="Space %s",
    sections=["space_metrics_by_appliance"],
    discovery_function=discovery_dell_powerstore_space,
    check_function=check_dell_powerstore_space,
    check_ruleset_name="param_dell_powerstore_space",
    check_default_parameters=Params(
        capacity=_Levels(
            perc_used=_DualLevels(
                lower=("no_levels", None),
                upper=("fixed", (80.0, 90.0)),
            ),
        ),
    ),
)
