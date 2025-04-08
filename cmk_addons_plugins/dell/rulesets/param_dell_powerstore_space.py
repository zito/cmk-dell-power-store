#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Generic, NotRequired, TypedDict, TypeVar

from cmk.rulesets.v1 import Help, rule_specs, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
    Levels,
    LevelsConfigModel,
    Percentage,
    PredictiveLevels,
)

_NumberT = TypeVar("_NumberT", int, float)


class _DualLevels(TypedDict, Generic[_NumberT]):
    upper: LevelsConfigModel[_NumberT]
    lower: LevelsConfigModel[_NumberT]

class _Levels(TypedDict):
    perc_used: NotRequired[_DualLevels[float]]

class Params(TypedDict):
    capacity: _Levels


def _perc_used_levels(title: Title, metric: str) -> Dictionary:
    return Dictionary(
        title=title,
        elements={
            "lower": DictElement(
                parameter_form=Levels[float](
                    title=Title("Lower levels"),
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.LOWER,
                    prefill_fixed_levels=DefaultValue((20.0, 10.0)),
                    predictive=PredictiveLevels(
                        reference_metric=metric,
                        prefill_abs_diff=DefaultValue((10.0, 20.0)),
                    ),
                ),
                required=False,
            ),
            "upper": DictElement(
                parameter_form=Levels[float](
                    title=Title("Upper levels"),
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue((80.0, 90.0)),
                    predictive=PredictiveLevels(
                        reference_metric=metric,
                        prefill_abs_diff=DefaultValue((10.0, 20.0)),
                    ),
                ),
                required=False,
            ),
        },
    )


def _param_form_dell_power_store_space() -> Dictionary:
    return Dictionary(
        elements={
            "capacity": DictElement(
                parameter_form=Dictionary(
                    title=Title("Space usage levels"),
                    elements={
                        "perc_used": DictElement(
                            parameter_form=_perc_used_levels(
                                Title("Space usage in percent"), "physical_used_percent"
                            ),
                        ),
                    },
                )
            ),
        },
    )


rule_spec_param_dell_powerstore_space = rule_specs.CheckParameters(
    name="param_dell_powerstore_space",
    title=Title("Levels for Physical Space Usage"),
    topic=rule_specs.Topic.OPERATING_SYSTEM,
    parameter_form=_param_form_dell_power_store_space,
    condition=rule_specs.HostAndItemCondition(item_title=Title("Appliance")),
)
