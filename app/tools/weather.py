from dataclasses import dataclass
from datetime import datetime

import requests


@dataclass
class WeatherData:
    latitude: float
    longitude: float
    timezone: str

    current_time: str
    temperature_c: float | None
    apparent_temperature_c: float | None
    precipitation_mm: float | None
    wind_speed_kmh: float | None

    forecast: list[dict]


class WeatherTool:

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
    ) -> WeatherData:

        if not -90 <= latitude <= 90:
            raise ValueError("Invalid latitude.")

        if not -180 <= longitude <= 180:
            raise ValueError("Invalid longitude.")

        if not 1 <= forecast_days <= 16:
            raise ValueError(
                "forecast_days must be between 1 and 16."
            )

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "precipitation,"
                "wind_speed_10m"
            ),
            "daily": (
                "temperature_2m_max,"
                "temperature_2m_min,"
                "precipitation_sum,"
                "precipitation_probability_max,"
                "weather_code"
            ),
            "forecast_days": forecast_days,
            "timezone": "auto",
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current", {})
        daily = data.get("daily", {})

        forecast = []

        dates = daily.get("time", [])
        max_temps = daily.get(
            "temperature_2m_max",
            [],
        )
        min_temps = daily.get(
            "temperature_2m_min",
            [],
        )
        precipitation = daily.get(
            "precipitation_sum",
            [],
        )
        precipitation_probability = daily.get(
            "precipitation_probability_max",
            [],
        )
        weather_codes = daily.get(
            "weather_code",
            [],
        )

        for index, date in enumerate(dates):

            forecast.append(
                {
                    "date": date,

                    "temperature_max_c":
                        self._get_value(
                            max_temps,
                            index,
                        ),

                    "temperature_min_c":
                        self._get_value(
                            min_temps,
                            index,
                        ),

                    "precipitation_mm":
                        self._get_value(
                            precipitation,
                            index,
                        ),

                    "precipitation_probability":
                        self._get_value(
                            precipitation_probability,
                            index,
                        ),

                    "weather_code":
                        self._get_value(
                            weather_codes,
                            index,
                        ),
                }
            )

        return WeatherData(
            latitude=data["latitude"],
            longitude=data["longitude"],
            timezone=data.get(
                "timezone",
                "UTC",
            ),
            current_time=current.get(
                "time",
                datetime.now().isoformat(),
            ),
            temperature_c=current.get(
                "temperature_2m"
            ),
            apparent_temperature_c=current.get(
                "apparent_temperature"
            ),
            precipitation_mm=current.get(
                "precipitation"
            ),
            wind_speed_kmh=current.get(
                "wind_speed_10m"
            ),
            forecast=forecast,
        )

    @staticmethod
    def _get_value(
        values: list,
        index: int,
    ):
        if index >= len(values):
            return None

        return values[index]


if __name__ == "__main__":

    tool = WeatherTool()

    # Manali coordinates
    weather = tool.get_weather(
        latitude=32.2432,
        longitude=77.1892,
        forecast_days=4,
    )

    print("WEATHER")
    print("=" * 40)

    print(
        "Current temperature:",
        weather.temperature_c,
        "°C",
    )

    print(
        "Feels like:",
        weather.apparent_temperature_c,
        "°C",
    )

    print(
        "Wind:",
        weather.wind_speed_kmh,
        "km/h",
    )

    print(
        "Timezone:",
        weather.timezone,
    )

    print("\nFORECAST")

    for day in weather.forecast:
        print(day)