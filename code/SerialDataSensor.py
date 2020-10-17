
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SerialDataSensor:
    light: int
    temperature: int
    timestamp: datetime
