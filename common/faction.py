from arrow import arrow


def get_faction_history_item(system_name, faction):
    ret_items = []

    # Add history
    for attribute, value in faction["influenceHistory"].items():
        # State history
        if type(faction["stateHistory"]) != list:
            state_history_value = next(
                (y for x, y in faction["stateHistory"].items() if x == attribute), None
            )
        else:
            state_history_value = None

        # Pending history
        if type(faction["pendingStatesHistory"]) != list:
            pending_state_history_value = next(
                (
                    y
                    for x, y in faction["pendingStatesHistory"].items()
                    if x == attribute
                ),
                None,
            )
        else:
            pending_state_history_value = None

        # Recovering states history
        if type(faction["recoveringStatesHistory"]) != list:
            recovering_state_history_value = next(
                (
                    y
                    for x, y in faction["recoveringStatesHistory"].items()
                    if x == attribute
                ),
                None,
            )
        else:
            recovering_state_history_value = None

        if state_history_value is None:
            continue
        ret_items.append(
            {
                "influence": value,
                "state": state_history_value,
                "system": system_name,
                "recovering_states": recovering_state_history_value,
                "pending_states": pending_state_history_value,
                "updated_at": arrow.Arrow.utcfromtimestamp(attribute).isoformat(),
                "updated_at_timestamp": attribute,
            }
        )
    ret_items.sort(key=lambda o: o["updated_at_timestamp"])

    # Add current state
    ret_items.append(
        {
            "influence": faction["influence"],
            "state": faction["state"],
            "system": system_name,
            "recovering_states": faction["recoveringStates"],
            "pending_states": faction["pendingStates"],
            "updated_at": arrow.Arrow.utcfromtimestamp(
                faction["lastUpdate"]
            ).isoformat(),
            "updated_at_timestamp": faction["lastUpdate"],
        }
    )
    return ret_items


def get_faction_state_name(internal_name):
    if internal_name is None or len(internal_name) == 0:
        return "Unknown"
    if internal_name == "civilunrest":
        return "Civil Unrest"
    elif internal_name == "civilwar":
        return "Civil War"
    return internal_name.capitalize()
