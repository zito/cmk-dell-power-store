#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""rule for assinging the special agent to host objects"""

# License: GNU General Public License v2

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    Password,
    String,
    migrate_to_password,
    validators,
)
from cmk.rulesets.v1.rule_specs import Topic, SpecialAgent


def _valuespec_special_agent_dell_powerstore() -> Dictionary:
    return Dictionary(
        title=Title("Dell PowerStore REST API"),
        elements={
            "user": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    custom_validate=(validators.LengthInRange(min_value=1),),
                    migrate=migrate_to_password,
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Advanced - TCP Port number"),
                    help_text=Help(
                        "Port number for connection to the Rest API. Usually 8443 (TLS)"
                    ),
                    prefill=DefaultValue(443),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=65535),),
                ),
            ),
            "timeout": DictElement(
                parameter_form=Integer(
                    title=Title("Advanced - Timeout for connection"),
                    help_text=Help(
                        "Number of seconds for a single connection attempt before timeout occurs."
                    ),
                    prefill=DefaultValue(30),
                    custom_validate=(validators.NumberInRange(min_value=1, max_value=60),),
                ),
            ),
        },
    )


rule_spec_dell_powerstore_datasource_programs = SpecialAgent(
    name="dell_powerstore",
    title=Title("Dell PowerStore"),
    topic=Topic.SERVER_HARDWARE,
    parameter_form=_valuespec_special_agent_dell_powerstore,
    help_text=(
        "This rule selects the Agent Dell PowerStore instead of the normal Check_MK Agent "
        "which collects the data through the PowerStore REST API"
    ),
)
