"""ReturnLoad learning exercise: match the order of stops on a fictional trip."""


def check_route(stops: list[str], pickup: str, dropoff: str) -> tuple[bool, str]:
    """Check exact stop names on a fixed route with no repeated stops."""
    if pickup == dropoff:
        return False, "Pickup and drop-off must be different."
    if pickup not in stops:
        return False, "Pickup is not on this trip."
    if dropoff not in stops:
        return False, "Drop-off is not on this trip."
    if stops.index(pickup) > stops.index(dropoff):
        return False, "This trip reaches the drop-off before the pickup."
    return True, "Pickup and drop-off are on the route in the right order."


def main() -> None:
    pickup = "Korangi"
    dropoff = "Clifton"
    trips = {
        "Trip A": ["Korangi", "Saddar", "Clifton"],
        "Trip B": ["Clifton", "Saddar", "Korangi"],
        "Trip C": ["Korangi", "Saddar"],
    }
    print(f"Fictional shipment: {pickup} -> {dropoff}")
    for name, stops in trips.items():
        matches, reason = check_route(stops, pickup, dropoff)
        status = "Route match" if matches else "Rejected"
        print(f"{name}: {status}. {reason}")


if __name__ == "__main__":
    main()
