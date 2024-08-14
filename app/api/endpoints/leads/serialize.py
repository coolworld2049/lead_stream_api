import numpy as np  # For handling NaN values


def set_for_keys(my_dict, key_arr, val):
    """
    Set val at path in my_dict defined by the string (or serializable object) array key_arr.
    If val is NaN, it is set to None.
    """
    # Convert NaN values to None
    if isinstance(val, (float, np.float64)) and np.isnan(val):
        val = None

    current = my_dict
    for i in range(len(key_arr)):
        key = key_arr[i]
        if key not in current:
            if i == len(key_arr) - 1:
                current[key] = val
            else:
                current[key] = {}
        else:
            if not isinstance(current[key], dict):
                raise ValueError(
                    "Dictionary key already occupied and is not a dictionary"
                )

        current = current[key]

    return my_dict


def to_formatted_json(df, sep="."):
    result = []
    for _, row in df.iterrows():
        parsed_row = {}
        for idx, val in row.items():
            keys = idx.split(sep)
            parsed_row = set_for_keys(parsed_row, keys, val)

        result.append(parsed_row)
    return result
