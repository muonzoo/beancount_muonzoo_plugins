#!/usr/bin/env python3
import ast


def parse(config_str):
    try:
        if len(config_str) != 0:
            conf_entity = ast.literal_eval(config_str)
        else:
            conf_entity = {}
    except:  # noqa: E722
        raise RuntimeError(f"Parsing failed: {config_str=}")

    if not isinstance(conf_entity, dict):
        raise RuntimeError(f"Plugin configuration wrong type {type(conf_entity)=}")

    return conf_entity
