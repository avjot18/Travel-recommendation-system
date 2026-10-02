from dataclasses import dataclass

from app.tools.geocoding import GeocodingTool
from app.tools.weather import WeatherTool, WeatherData


@dataclass
class DestinationWeather:
    destination: str
    state: str | None
    weather: WeatherData


class DestinationWeatherTool:

    def __init__(
        self,
        geocoding_tool: GeocodingTool | None = None,
        weather_tool: WeatherTool | None = None,
    ):
        self.geocoding_tool = (
            geocoding_tool
            or GeocodingTool()
        )

        self.weather_tool = (
            weather_tool
            or WeatherTool()
        )

    def get_weather(
        self,
        destination: str,
        state: str | None = None,
        forecast_days: int = 7,
    ) -> DestinationWeather:

        location = self.geocoding_tool.search(
            query=destination,
            state=state,
        )

        if location is None:
            raise ValueError(
                f"Could not resolve destination: "
                f"{destination}"
            )

        weather = self.weather_tool.get_weather(
            latitude=location.latitude,
            longitude=location.longitude,
            forecast_days=forecast_days,
        )

        return DestinationWeather(
            destination=location.name,
            state=location.admin1,
            weather=weather,
        )


if __name__ == "__main__":

    tool = DestinationWeatherTool()

    result = tool.get_weather(
        destination="Manali",
        state="Himachal Pradesh",
        forecast_days=4,
    )

    print("DESTINATION WEATHER")
    print("=" * 50)

    print(
        "Destination:",
        result.destination,
    )

    print(
        "State:",
        result.state,
    )

    print(
        "Temperature:",
        result.weather.temperature_c,
        "°C",
    )

    print(
        "Feels like:",
        result.weather.apparent_temperature_c,
        "°C",
    )

    print(
        "Wind:",
        result.weather.wind_speed_kmh,
        "km/h",
    )

    print("\nFORECAST")

    for day in result.weather.forecast:
        print(day)