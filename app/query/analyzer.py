import json

from langchain_ollama import ChatOllama

from app.query.models import TravelProfile


class QueryAnalyzer:

    def __init__(
        self,
        model_name: str = "qwen3:1.7b",
    ):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0,
        )

    def analyze(
        self,
        query: str,
    ) -> TravelProfile:

        prompt = self._build_prompt(query)

        response = self.llm.invoke(prompt)

        return self._parse_response(
            response
        )

    def _build_prompt(
        self,
        query: str,
    ) -> str:

        return f"""
You are the query understanding component
of a travel planning system.

Analyze the user's travel request and extract
structured requirements.

USER QUERY:
--------------------
{query}
--------------------

Return ONLY valid JSON.

Use this exact structure:

{{
    "intent": "",
    "trip_type": null,
    "location": null,
    "duration_days": null,
    "budget_range": null,
    "season": null,
    "travelers": [],
    "travel_styles": [],
    "interests": [],
    "activities": [],
    "pace": null,
    "preferred_region": null,
    "must_have_activities": [],
    "avoids": [],
    "needs_live_weather": false
}}

IMPORTANT RULES:

1. Extract only information supported by the
   user's query.

2. Do not invent missing information.

3. duration_days must be an integer when the
   user gives a trip duration.

4. budget_range should capture explicit budget
   information such as:
   "low", "mid-range", "luxury".

5. travelers should contain categories such as:
   "solo", "couple", "family", "friends".

6. travel_styles should capture styles such as:
   "mountain", "beach", "adventure",
   "peaceful", "scenic", "cultural",
   "wellness".

7. must_have_activities should contain activities
   the user explicitly requires.

8. avoids should contain things the user explicitly
   wants to avoid.

9. needs_live_weather must be TRUE only when the
   user requires CURRENT or FORECAST weather
   information to answer their request.

10. Set needs_live_weather=true when the user asks
    about things such as:
    - current weather
    - upcoming weather
    - forecast
    - expected rain
    - expected snow
    - expected temperature
    - weather conditions affecting a trip
    - whether weather conditions make a trip suitable

11. Do NOT set needs_live_weather=true merely
    because the user mentions:
    - a season
    - climate generally
    - temperature preferences
    - avoiding extreme cold
    - wanting summer/winter travel

12. If historical or general climate information
    is sufficient, needs_live_weather should remain
    false.

13. The distinction is:

    GENERAL / HISTORICAL INFORMATION
    -> needs_live_weather=false

    CURRENT / FUTURE CONDITIONS
    -> needs_live_weather=true

14. intent should describe the user's MAIN request.

    Possible intents are:

    - destination_recommendation
    - destination_comparison
    - trip_planning
    - weather_information
    - attraction_search
    - activity_search
    - general_travel_question

15. Use intent="weather_information" when the
    PRIMARY purpose of the query is to obtain
    current or forecast weather information for
    a specific destination.

    Examples:

    "What is the weather in Manali?"
    -> intent="weather_information"
    -> needs_live_weather=true

    "What will the weather be like in Manali
     next weekend?"
    -> intent="weather_information"
    -> needs_live_weather=true

    "Will it snow in Gulmarg next week?"
    -> intent="weather_information"
    -> needs_live_weather=true

16. If the user's PRIMARY purpose is trip planning
    and weather is only one requirement, use
    intent="trip_planning" and set
    needs_live_weather=true.

    Example:

    "I want to visit Manali next weekend. Will the
     weather be suitable?"

    -> intent="trip_planning"
    -> location="Manali"
    -> needs_live_weather=true

17. If the user is asking for destination
    recommendations and mentions weather only as
    a preference, do NOT classify the query as
    weather_information.

    Example:

    "I want a mountain trip but I don't want
     extreme cold."

    -> intent="destination_recommendation"
    -> needs_live_weather=false

18. If a specific destination is explicitly named,
    extract it into the "location" field.

    Example:

    "What will the weather be like in Manali?"
    -> location="Manali"

19. Do not invent a location.

    If no destination or location is explicitly
    provided, keep:

    "location": null

20. When intent="weather_information", the location
    should contain the destination for which the
    weather is requested, if explicitly provided.

21. Do not confuse general temperature preferences
    with a request for live weather.

    Example:

    "I don't want extreme cold."
    -> needs_live_weather=false

    Example:

    "Will it be extremely cold in Manali next week?"
    -> needs_live_weather=true

22. Return ONLY the JSON object.
Do not include explanations.
Do not include markdown.
Do not include code fences.

Return ONLY JSON.
"""

    def _parse_response(
        self,
        response,
    ) -> TravelProfile:

        content = response.content

        if not isinstance(
            content,
            str,
        ):
            content = str(content)

        content = content.strip()

        content = self._remove_code_fences(
            content
        )

        try:
            data = json.loads(content)

        except json.JSONDecodeError as error:

            raise ValueError(
                "Query analyzer did not return "
                "valid JSON."
            ) from error

        return TravelProfile.model_validate(
            data
        )

    @staticmethod
    def _remove_code_fences(
        content: str,
    ) -> str:

        if not content.startswith("```"):
            return content.strip()

        lines = content.splitlines()

        if lines:
            lines = lines[1:]

        if (
            lines
            and lines[-1].strip() == "```"
        ):
            lines = lines[:-1]

        return "\n".join(
            lines
        ).strip()


if __name__ == "__main__":

    analyzer = QueryAnalyzer()

    queries = [

        "What will the weather be like "
        "in Manali next weekend?",

        "I have 4 days and want a peaceful "
        "mountain trip with my girlfriend.",

        "Will it snow in Gulmarg next week?",

        "I want to avoid extreme cold "
        "on my mountain trip.",
    ]

    for query in queries:

        print("\n" + "=" * 60)

        print("QUERY:")
        print(query)

        result = analyzer.analyze(
            query
        )

        print("\nPROFILE:")

        print(
            result.model_dump_json(
                indent=2
            )
        )