import numpy as np
from ..models.environment import WeatherState


class EnvironmentSubsystem:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def step(self, weather: WeatherState, delta_hours: float):
        """
        Advance weather dynamics with polar micro-fluctuations.
        """
        # Ambient temperature fluctuation (+-0.2C jitter, colder during storms)
        jitter_temp = self.rng.normal(0.0, 0.15)
        if weather.storm_active:
            target_temp = -38.0
            target_wind = 75.0
            weather.visibility_km = max(0.2, weather.visibility_km - 1.5 * delta_hours)
        else:
            target_temp = -25.0
            target_wind = 15.0
            weather.visibility_km = min(15.0, weather.visibility_km + 0.5 * delta_hours)

        # Smooth drift towards target
        weather.ambient_temp_c += (target_temp - weather.ambient_temp_c) * 0.05 * delta_hours + jitter_temp
        weather.ambient_temp_c = round(weather.ambient_temp_c, 2)

        # Wind speed fluctuation
        jitter_wind = self.rng.normal(0.0, 1.0)
        weather.wind_speed_kmh += (target_wind - weather.wind_speed_kmh) * 0.1 * delta_hours + jitter_wind
        weather.wind_speed_kmh = max(2.0, round(weather.wind_speed_kmh, 1))

        if weather.wind_speed_kmh > 50.0:
            weather.storm_active = True
            weather.condition_summary = f"Blizzard / Gale ({weather.wind_speed_kmh} km/h)"
        else:
            weather.storm_active = False
            weather.condition_summary = f"Nominal Polar ({weather.ambient_temp_c} C, {weather.wind_speed_kmh} km/h)"
