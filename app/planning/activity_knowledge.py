class ActivityKnowledge:

    STYLE_COMPATIBILITY = {

        "adventure": {
            "trekking",
            "hiking",
            "skiing",
            "rafting",
            "camping",
            "paragliding"
        },

        "peaceful": {
            "sightseeing",
            "photography",
            "nature",
            "meditation",
            "yoga"
        },

        "scenic": {
            "sightseeing",
            "photography",
            "nature"
        },

        "wellness": {
            "yoga",
            "meditation"
        },

        "cultural": {
            "sightseeing",
            "heritage",
            "cultural exploration"
        }
    }

    @classmethod
    def activities_for_style(
        cls,
        style: str
    ) -> set[str]:

        return cls.STYLE_COMPATIBILITY.get(
            style.lower(),
            set()
        )