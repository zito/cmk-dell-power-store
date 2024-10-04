#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
"""server side component to create the special agent call"""

# License: GNU General Public License v2

from collections.abc import Iterator
from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)


class Params(BaseModel):
    """params validator"""
    user: str | None = None
    password: Secret | None = None
    port: int | None = None
    timeout: int | None = None


def _agent_dell_powerstore_arguments(
    params: Params, host_config: HostConfig
) -> Iterator[SpecialAgentCommand]:
    command_arguments: list[str | Secret] = []
    if params.user is not None:
        command_arguments += ["-u", params.user]
    if params.password is not None:
        command_arguments += ["--password-id", params.password]
    if params.port is not None:
        command_arguments += ["-p", str(params.port)]
    if params.timeout is not None:
        command_arguments += ["-t", str(params.timeout)]
    command_arguments.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=command_arguments)


special_agent_dell_powerstore = SpecialAgentConfig(
    name="dell_powerstore",
    parameter_parser=Params.model_validate,
    commands_function=_agent_dell_powerstore_arguments,
)
