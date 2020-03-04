import datetime
import re


def timestamp_to_date(input_str):
    date = int(input_str) if input_str is not None else None

    if date is not None:
        date = datetime.datetime.fromtimestamp(date)

    return date


def get_name_or_unknown(internal_name):
    if internal_name is None or len(internal_name) == 0:
        return "Unknown"
    return internal_name.title()


def get_name_or_unknown_from_obj(internal_name, obj_with_infos):
    if (
        internal_name is None
        or len(internal_name) == 0
        or obj_with_infos is None
        or getattr(obj_with_infos, internal_name) is None
    ):
        return "Unknown"
    return getattr(obj_with_infos, internal_name).title()
