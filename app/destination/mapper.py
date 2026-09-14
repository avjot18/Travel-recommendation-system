from app.destination.repository import (
    DestinationRepository
)


class DestinationMapper:

    def __init__(
        self,
        repository: DestinationRepository
    ):

        self.repository = repository

    def document_to_profile(
        self,
        document
    ):

        destination_id = (
            document.metadata.get(
                "destination_id"
            )
        )

        if not destination_id:
            return None

        return self.repository.get_destination(
            destination_id
        )

    def documents_to_profiles(
        self,
        documents
    ):

        profiles = []

        seen_ids = set()

        for document in documents:

            profile = self.document_to_profile(
                document
            )

            if profile is None:
                continue

            if (
                profile.destination_id
                in seen_ids
            ):
                continue

            profiles.append(profile)

            seen_ids.add(
                profile.destination_id
            )

        return profiles