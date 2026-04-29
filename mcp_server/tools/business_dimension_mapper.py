import difflib
from mcp_server.tools.business_dimensions import (
    extract_business_dimensions
)


class DimensionValueMapper:
    """
    Corrects user-entered business dimension values
    against actual database dimension values.

    Example:
    distributor -> Distributors
    cairo -> Cairo Branch
    salesman 1 -> SalesmanName 1
    """

    def __init__(self):
        self.dimensions = extract_business_dimensions()

    def normalize_text(self, text: str):
        return text.lower().strip()

    def find_best_match(
        self,
        user_value: str,
        possible_values: list,
        cutoff: float = 0.7
    ):
        normalized_map = {
            self.normalize_text(v): v
            for v in possible_values
        }

        matches = difflib.get_close_matches(
            self.normalize_text(user_value),
            normalized_map.keys(),
            n=1,
            cutoff=cutoff
        )

        if matches:
            return normalized_map[matches[0]]

        return user_value

    def correct_filters(
        self,
        extracted_filters: dict
    ):
        corrected = {}

        DIMENSION_MAPPING = {
            "Branch": "branches",
            "Salesman": "salesmen",
            "Region": "regions",
            "District": "districts",
            "City": "cities",
            "Area": "areas",

            "Customer Channel": "customer_category",
            "Customer Sub-Channel": "customer_category2",
            "Customer Level 3": "customer_category3",
            "Customer Level 4": "customer_category4",

            "Master Brand": "item_category1",
            "Sub Brand": "item_category2",
            "Item Level 3": "item_category3",
            "Item Level 4": "item_category4",

            "Company": "company_codes"
        }

        for dimension, value in extracted_filters.items():

            db_dimension_key = DIMENSION_MAPPING.get(
                dimension
            )

            if not db_dimension_key:
                corrected[dimension] = value
                continue

            possible_values = self.dimensions.get(
                db_dimension_key,
                []
            )

            corrected_value = self.find_best_match(
                value,
                possible_values
            )

            corrected[dimension] = corrected_value

        return corrected


def correct_user_dimension_filters(
    filters: dict
):
    mapper = DimensionValueMapper()

    return mapper.correct_filters(
        filters
    )