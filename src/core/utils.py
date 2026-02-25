def to_dict(vals):
    """
    Standardizes input data into a list of dictionaries.
    """
    if isinstance(vals, list):
        vals = [
            item.model_dump() if hasattr(item, "model_dump") else item for item in vals
        ]
    else:
        vals = [vals.model_dump() if hasattr(vals, "model_dump") else vals]
    return vals
