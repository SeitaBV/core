"""S2 Control types for the CEM."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass
class FRBC_Config:
    """Dataclass for FRBC configuration."""

    power_sensor_id: int
    price_sensor_id: int
    soc_sensor_id: int
    rm_discharge_sensor_id: int
    schedule_duration: timedelta
