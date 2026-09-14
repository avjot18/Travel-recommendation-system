import re


class DestinationNormalizer:

    def normalize_duration(
        self,
        duration
    ) -> list[int]:

        if duration is None:
            return []

        if isinstance(duration, list):

            numbers = []

            for value in duration:
                try:
                    numbers.append(
                        int(value)
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    continue

            return numbers

        if isinstance(duration, str):

            numbers = re.findall(
                r"\d+",
                duration
            )

            return [
                int(number)
                for number in numbers
            ]

        if isinstance(duration, int):

            return [duration]

        return []