class QueryRewriter:

    def rewrite(self, travel_profile):

        parts = []

        if travel_profile.location:
            parts.append(travel_profile.location)

        if travel_profile.preferred_region:
            parts.append(travel_profile.preferred_region)

        if travel_profile.duration_days:
            parts.append(
                f"{travel_profile.duration_days} day trip"
            )

        if travel_profile.budget_range:
            parts.append(
                f"{travel_profile.budget_range} budget"
            )

        if travel_profile.trip_type:
            parts.append(travel_profile.trip_type)

        if travel_profile.travelers:
            parts.extend(travel_profile.travelers)

        if travel_profile.travel_styles:
            parts.extend(travel_profile.travel_styles)

        if travel_profile.interests:
            parts.extend(travel_profile.interests)

        if travel_profile.activities:
            parts.extend(travel_profile.activities)

        if travel_profile.pace:
            parts.append(travel_profile.pace)

        if travel_profile.must_have_activities:
            parts.extend(
                f"must have {activity}"
                for activity
                in travel_profile.must_have_activities
            )

        if travel_profile.avoids:
            parts.extend(
                f"avoid {avoid}"
                for avoid
                in travel_profile.avoids
            )

        return " ".join(parts)