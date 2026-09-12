from langchain_core.documents import Document


class TravelDocumentBuilder:

    def build_destination_documents(
        self,
        destinations: list[dict]
    ) -> list[Document]:

        documents = []

        for destination in destinations:

            destination_id = destination.get("destination_id")

            content = f"""
Destination: {destination.get("name")}
State: {destination.get("state_or_ut")}
Region: {destination.get("region")}

Description:
{destination.get("description")}

Travel Styles:
{", ".join(destination.get("travel_styles", []))}

Best For:
{", ".join(destination.get("best_for", []))}

Best Months:
{", ".join(destination.get("best_months", []))}

Ideal Duration:
{destination.get("ideal_duration_days")}

Budget:
{destination.get("budget_tier")}

Activities:
{", ".join(destination.get("activities", []))}

Food:
{", ".join(destination.get("food_highlights", []))}

Pros:
{", ".join(destination.get("pros", []))}

Cons:
{", ".join(destination.get("cons", []))}

Planning Notes:
{destination.get("notes")}
""".strip()

            metadata = {
    "entity_type": "destination",
    "destination_id": destination_id,
    "destination": destination.get("name"),
    "state": destination.get("state_or_ut"),
    "region": destination.get("region"),

    "travel_styles": destination.get("travel_styles", []),
    "best_for": destination.get("best_for", []),
    "budget_tier": destination.get("budget_tier"),
    "ideal_duration_days": destination.get("ideal_duration_days"),
    "activities": destination.get("activities", []),

    "data_quality": destination.get("data_quality"),
    "verification_status": destination.get("verification_status"),
}

            documents.append(
                Document(
                    id=f"destination-{destination_id}",
                    page_content=content,
                    metadata=metadata
                )
            )

        return documents

    def build_attraction_documents(
        self,
        attractions: list[dict]
    ) -> list[Document]:

        documents = []

        for index, attraction in enumerate(attractions):

            attraction_name = attraction.get("name")

            content = f"""
Attraction: {attraction_name}

Description:
{attraction.get("description")}

Search Tags:
{", ".join(attraction.get("search_tags", []))}

Destination ID:
{attraction.get("destination_id")}

Notes:
{attraction.get("notes")}
""".strip()

            metadata = {
                "entity_type": "attraction",
                "attraction": attraction_name,
                "destination_id": attraction.get("destination_id"),
                "data_quality": attraction.get("data_quality"),
                "verification_status": attraction.get("verification_status"),
            }

            documents.append(
                Document(
                    id=f"attraction-{index}-{attraction_name}",
                    page_content=content,
                    metadata=metadata
                )
            )

        return documents