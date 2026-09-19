from dataclasses import dataclass


@dataclass
class SimulationClock:
    minutes_per_tick: int = 1
    current_tick: int = 0

    def tick(self) -> int:
        self.current_tick += 1
        return self.current_tick

    def reset(self, start_tick: int = 0):
        self.current_tick = start_tick

    @property
    def total_elapsed_minutes(self) -> int:
        return self.current_tick * self.minutes_per_tick

    @property
    def formatted_sim_time(self) -> str:
        total_mins = self.total_elapsed_minutes
        days = total_mins // (24 * 60)
        rem_mins = total_mins % (24 * 60)
        hours = rem_mins // 60
        mins = rem_mins % 60
        return f"Day {days + 1:02d} {hours:02d}:{mins:02d}"

    @property
    def delta_days(self) -> float:
        return self.minutes_per_tick / (24.0 * 60.0)

    @property
    def delta_hours(self) -> float:
        return self.minutes_per_tick / 60.0
