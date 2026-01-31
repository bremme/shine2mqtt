def merge_dict(base: dict, override: dict) -> dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dict(result[key], value)
        else:
            result[key] = value
    return result


def remove_none_values(dict_with_none: dict) -> dict:
    return {k: v for k, v in dict_with_none.items() if v is not None}


def convert_to_nested_dict(flat_dict: dict, delimiter: str = "__") -> dict:
    nested_dict = {}
    for key, value in flat_dict.items():
        if delimiter in key:
            parts = key.split(delimiter)
            current = nested_dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = value
        else:
            nested_dict[key] = value
    return nested_dict
