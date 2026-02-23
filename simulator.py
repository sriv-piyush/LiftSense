from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import math

@dataclass
class Elevator:
    id: int
    current_floor: int
    direction: str              # 'up', 'down', 'idle'
    state: str                  # 'operational' or 'out_of_service'
    stops: List[int] = field(default_factory=list)
    load: float = 0.0           # 0.0 (empty) to 1.0 (full)
    door_time: int = 2
    speed: float = 1.0

    def eta_to(self, request_floor: int) -> float:
        if self.state != 'operational':
            return math.inf

        pos = self.current_floor
        t = 0.0

        if self.direction == 'idle' and not self.stops:
            return abs(pos - request_floor) / self.speed

        simulated = self.stops.copy()
        while simulated:
            next_stop = simulated.pop(0)
            t += abs(pos - next_stop) / self.speed
            pos = next_stop
            t += self.door_time
            if pos == request_floor:
                return t

        t += abs(pos - request_floor) / self.speed
        return t

    def score(self, request_floor: int, emergency: bool = False) -> float:
        if self.state != 'operational':
            return math.inf

        eta = self.eta_to(request_floor)
        stop_penalty = len(self.stops) * 1.5
        load_penalty = self.load * 10

        score = eta + stop_penalty + load_penalty

        if emergency:
            score = eta * 0.4

        return score

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'current_floor': self.current_floor,
            'direction': self.direction,
            'state': self.state,
            'stops': self.stops.copy(),
            'load': self.load
        }


class BuildingSimulator:
    def __init__(self, n_elevators=4, top_floor=20, seed: Optional[int] = None):
        self.top_floor = top_floor

        # 🔥 FIXED DEMO POSITIONS (as requested)
        self.elevators: List[Elevator] = [
            Elevator(
                id=1,
                current_floor=18,
                direction='idle',
                state='operational',
                stops=[20],
                load=0.4
            ),
            Elevator(
                id=2,
                current_floor=6,
                direction='up',
                state='operational',
                stops=[9, 12],
                load=0.7
            ),
            Elevator(
                id=3,
                current_floor=13,
                direction='down',
                state='operational',
                stops=[10],
                load=0.2
            ),
            Elevator(
                id=4,
                current_floor=2,
                direction='up',
                state='operational',
                stops=[5],
                load=0.5
            )
        ]

    def get_state(self) -> Dict[str, Any]:
        return {'elevators': [e.to_dict() for e in self.elevators]}

    def recommend(
        self,
        request_floor: int,
        request_direction: Optional[str] = None,
        emergency: bool = False
    ) -> Dict[str, Any]:

        scored = []
        for e in self.elevators:
            score = e.score(request_floor, emergency)
            scored.append((e, score))

        scored.sort(key=lambda x: (x[1], x[0].id))
        best = scored[0][0]

        return {
            'request_floor': request_floor,
            'request_direction': request_direction,
            'emergency_mode': emergency,
            'evaluated_elevators': [
                {
                    'id': e.id,
                    'eta': None if e.eta_to(request_floor) == math.inf else round(e.eta_to(request_floor), 2),
                    'stops': len(e.stops),
                    'load': e.load,
                    'state': e.state,
                    'score': None if score == math.inf else round(score, 2)
                }
                for e, score in scored
            ],
            'best': {
                'id': best.id,
                'current_floor': best.current_floor,
                'load': best.load
            }
        }

    def step_simulation(self):
        for e in self.elevators:
            if e.state != 'operational':
                continue

            if e.stops:
                target = e.stops[0]
                if e.current_floor < target:
                    e.current_floor += 1
                    e.direction = 'up'
                elif e.current_floor > target:
                    e.current_floor -= 1
                    e.direction = 'down'
                else:
                    e.stops.pop(0)
                    e.direction = 'idle' if not e.stops else e.direction
            else:
                e.direction = 'idle'
