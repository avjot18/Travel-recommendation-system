class AnswerGenerator:

    def __init__(self, model_name: str = None):
        pass

    def generate(
        self,
        query,
        query_analysis,
        recommendation_decision=None,
        destination_weather=None,
        destination_profile=None,
        activity_plan=None,
        itinerary_plan=None,
        budget_plan=None,
        stay_area_plan=None,
    ):

        # -------------------------------------------------
        # WEATHER INFORMATION
        # -------------------------------------------------

        if (
            query_analysis.intent
            == "weather_information"
        ):

            return self._generate_weather_answer(
                destination_weather
            )

        # -------------------------------------------------
        # RECOMMENDATION / TRIP PLANNING
        # -------------------------------------------------

        if not recommendation_decision:

            return (
                "I could not find a suitable destination "
                "from the available data."
            )

        candidate = recommendation_decision.get(
            "candidate"
        )

        if not candidate:

            return (
                "I could not find a suitable destination "
                "from the available data."
            )

        document = candidate["document"]
        metadata = document.metadata
        fit = candidate["requirement_fit"]

        destination = metadata.get(
            "destination"
        )

        duration = metadata.get(
            "ideal_duration_days"
        )

        direct_matches = fit.get(
            "direct_matches",
            []
        )

        semantic_matches = fit.get(
            "semantic_matches",
            []
        )

        possible_matches = fit.get(
            "possible_matches",
            []
        )

        unknowns = fit.get(
            "unknowns",
            []
        )

        mismatches = fit.get(
            "mismatches",
            []
        )

        why = []

        # -------------------------------------------------
        # Duration
        # -------------------------------------------------

        if (
            "duration" in direct_matches
            and duration
        ):

            if (
                isinstance(duration, list)
                and len(duration) >= 2
            ):

                why.append(
                    f"Your "
                    f"{query_analysis.duration_days}-day trip "
                    f"fits the listed ideal duration of "
                    f"{duration[0]}–{duration[1]} days."
                )

            else:

                why.append(
                    f"Your "
                    f"{query_analysis.duration_days}-day trip "
                    f"matches the listed ideal duration."
                )

        # -------------------------------------------------
        # Travelers
        # -------------------------------------------------

        for traveler in query_analysis.travelers:

            if traveler in direct_matches:

                why.append(
                    f"{destination} is explicitly listed as "
                    f"suitable for {traveler}."
                )

        # -------------------------------------------------
        # Semantic matches
        # -------------------------------------------------

        for match in semantic_matches:

            why.append(
                f"The available data shows a possible match "
                f"for {match}."
            )

        # -------------------------------------------------
        # Possible matches
        # -------------------------------------------------

        if "location" in possible_matches:

            why.append(
                "The destination is a possible match for "
                "your requested mountain setting."
            )

        # -------------------------------------------------
        # Fallback
        # -------------------------------------------------

        if not why:

            why.append(
                "It is the highest-ranked available candidate "
                "for your requirements."
            )

        # -------------------------------------------------
        # Limitations
        # -------------------------------------------------

        limitations = []

        for unknown in unknowns:

            if unknown == "peaceful":

                limitations.append(
                    "The current data does not verify whether "
                    "the destination is peaceful."
                )

            elif unknown == "extreme cold avoidance":

                limitations.append(
                    "The current data does not verify whether "
                    "extreme cold can be avoided."
                )

            elif unknown == "budget":

                limitations.append(
                    "The current data does not verify whether "
                    "the destination fits your budget."
                )

            elif "suitability" in unknown:

                limitations.append(
                    f"The current data does not fully verify "
                    f"{unknown}."
                )

            else:

                limitations.append(
                    f"The current data does not verify "
                    f"{unknown}."
                )

        # -------------------------------------------------
        # Actual mismatches
        # -------------------------------------------------

        for mismatch in mismatches:

            limitations.append(
                f"The destination does not match your "
                f"{mismatch} requirement."
            )

        # -------------------------------------------------
        # Recommendation answer
        # -------------------------------------------------

        answer = (
            f"Recommendation: {destination}\n\n"
        )

        answer += "Why:\n"

        for reason in why:

            answer += (
                f"- {reason}\n"
            )

        if limitations:

            answer += "\nLimitations:\n"

            for limitation in limitations:

                answer += (
                    f"- {limitation}\n"
                )

        return answer.strip()

    # =================================================
    # WEATHER ANSWER
    # =================================================

    def _generate_weather_answer(
        self,
        destination_weather
    ):

        if destination_weather is None:

            return (
                "I could not retrieve live weather "
                "information for the requested destination."
            )

        destination = (
            destination_weather.destination
        )

        weather = (
            destination_weather.weather
        )

        answer = (
            f"Weather for {destination}\n\n"
        )

        # -------------------------------------------------
        # Current conditions
        # -------------------------------------------------

        answer += "Current conditions:\n"

        if (
            weather.temperature_c
            is not None
        ):

            answer += (
                f"- Temperature: "
                f"{weather.temperature_c} °C\n"
            )

        if (
            weather.apparent_temperature_c
            is not None
        ):

            answer += (
                f"- Feels like: "
                f"{weather.apparent_temperature_c} °C\n"
            )

        if (
            weather.precipitation_mm
            is not None
        ):

            answer += (
                f"- Precipitation: "
                f"{weather.precipitation_mm} mm\n"
            )

        if (
            weather.wind_speed_kmh
            is not None
        ):

            answer += (
                f"- Wind speed: "
                f"{weather.wind_speed_kmh} km/h\n"
            )

        # -------------------------------------------------
        # Forecast
        # -------------------------------------------------

        forecast = getattr(
            weather,
            "forecast",
            []
        )

        if forecast:

            answer += "\nForecast:\n"

            for day in forecast:

                if isinstance(day, dict):

                    date = day.get(
                        "date",
                        "Unknown date"
                    )

                    temperature = day.get(
                        "temperature_c"
                    )

                    precipitation = day.get(
                        "precipitation_mm"
                    )

                    line = (
                        f"- {date}"
                    )

                    if temperature is not None:

                        line += (
                            f": {temperature} °C"
                        )

                    if precipitation is not None:

                        line += (
                            f", precipitation "
                            f"{precipitation} mm"
                        )

                    answer += (
                        line + "\n"
                    )

                else:

                    answer += (
                        f"- {day}\n"
                    )

        return answer.strip()