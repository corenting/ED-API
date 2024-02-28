import csv

from app.constants import DATA_PATH
from app.models.outfitting import Outfitting


class OutfittingService:
    def __init__(self) -> None:
        self.outfitting = self._parse_outfitting_csv()

    def _parse_outfitting_csv(self) -> list[Outfitting]:
        items: list[Outfitting] = []
        with open(DATA_PATH + "/outfitting.csv") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            items.extend(
                Outfitting(
                    id=int(row["id"]),
                    symbol=row["symbol"],
                    category=row["category"],
                    name=row["name"],
                    mount=row["mount"],
                    guidance=row["guidance"],
                    ship=row["ship"],
                    outfitting_class=int(row["class"]),
                    outfitting_rating=row["rating"],
                    display_name="",
                )
                for row in csv_reader
            )

        # Compute display names
        for item in items:
            item.display_name = self._get_display_name_for_outfitting(item)

        return items

    def _get_display_name_for_outfitting(self, outfitting: Outfitting) -> str:
        """
        Get a display name for the specified outfitting item.
        """
        name = ""
        if outfitting.outfitting_class:
            name += f"[{outfitting.outfitting_class}{outfitting.outfitting_rating}] "

        name += outfitting.name
        if outfitting.mount:
            guidance = f"{outfitting.guidance}, " if outfitting.guidance else ""
            name += f" ({guidance}{outfitting.mount})"
        elif outfitting.ship:
            name += f" ({outfitting.ship})"

        return name

    def get_outfitting_typeahead(self, input_text: str) -> list[str]:
        """
        Return a list of outfitting matching the input
        """
        return [
            item.display_name
            for item in self.outfitting
            if input_text.lower().strip() in item.display_name.lower()
        ]
