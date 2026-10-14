"""Strict, bounded contracts. Unknown cost fields are rejected, never ignored."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator

class Model(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)

class Batch(Model):
    id: str = Field(min_length=1, max_length=80)
    produce: str = Field(min_length=1, max_length=80)
    grade: str = 'A'
    quantity: float = Field(ge=0, le=100000)
    unit: Literal['kg'] = 'kg'
    received: AwareDatetime
    expiry: AwareDatetime
    acquisition: float = Field(ge=0, le=100000)
    source: str = 'Synthetic demo'

class Demand(Model):
    produce: str = Field(min_length=1, max_length=80)
    quantity: float = Field(ge=0, le=100000)
    maximum: float = Field(ge=0, le=100000)
    price: float = Field(ge=0, le=100000)
    minimumPrice: float = Field(ge=0, le=100000)
    priority: int = Field(default=1, ge=1, le=5)
    @model_validator(mode='after')
    def limits(self):
        if self.quantity > self.maximum: raise ValueError('Demand cannot exceed maximum acceptable quantity')
        if self.minimumPrice > self.price: raise ValueError('Minimum price cannot exceed selling price')
        return self

class Destination(Model):
    id: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=80)
    opens: AwareDatetime
    closes: AwareDatetime
    demands: list[Demand] = Field(min_length=1, max_length=10)
    @model_validator(mode='after')
    def limits(self):
        if self.closes < self.opens: raise ValueError('Receiving window end precedes start')
        if len({d.produce for d in self.demands}) != len(self.demands): raise ValueError('Duplicate produce demand')
        return self

class Route(Model):
    id: str = Field(min_length=1, max_length=80)
    origin: str = 'FreshRoute hub'
    destination: str
    travel: float = Field(ge=0, le=168)
    delay: float = Field(ge=0, le=168)
    handling: float = Field(ge=0, le=168)
    capacity: float = Field(ge=0, le=100000)
    unit: Literal['kg'] = 'kg'
    fixedCost: float = Field(ge=0, le=100000)
    perKg: float = Field(ge=0, le=10000)
    handlingCost: float = Field(ge=0, le=10000)
    eligible: list[str] = Field(default_factory=list)

class Scenario(Model):
    id: str
    name: str = Field(min_length=1, max_length=100)
    synthetic: bool = True
    planningTime: AwareDatetime
    horizonHours: float = Field(gt=0, le=168)
    currency: Literal['INR'] = 'INR'
    maxDiscount: float = Field(ge=0, le=0.5)
    riskHours: float = Field(ge=0, le=168)
    disposalPerKg: float = Field(ge=0, le=10000)
    packagingPerKg: float | None = Field(default=None, ge=0, le=10000)
    storagePerKg: float | None = Field(default=None, ge=0, le=10000)
    platformRate: float | None = Field(default=None, ge=0, le=1)
    taxRate: float | None = Field(default=None, ge=0, le=1)
    applyDiscounts: bool = False
    batches: list[Batch] = Field(min_length=1, max_length=30)
    destinations: list[Destination] = Field(min_length=1, max_length=6)
    routes: list[Route] = Field(min_length=1, max_length=6)
    @model_validator(mode='after')
    def integrity(self):
        for rows in [self.batches, self.destinations, self.routes]:
            if len({r.id for r in rows}) != len(rows): raise ValueError('IDs must be unique within each table')
        dests = {d.id for d in self.destinations}
        if any(r.destination not in dests for r in self.routes): raise ValueError('Route references unknown destination')
        for b in self.batches:
            if b.received > self.planningTime: raise ValueError(f'{b.id}: received time is after planning time')
            if b.expiry < b.received: raise ValueError(f'{b.id}: expiry is before receipt')
        return self

Objective = Literal['contribution', 'balanced', 'spoilage']
class PlanRequest(Model):
    scenario: Scenario
    objective: Objective = 'contribution'

class Allocation(Model):
    batch: str
    produce: str
    destination: str
    destinationName: str
    route: str
    quantity: float
    price: float
    originalPrice: float
    discount: float
    departure: datetime
    arrival: datetime
    usable: datetime
    latestDeparture: datetime
    expiry: datetime
    slackHours: float
    urgency: int
    reason: str

class Metrics(Model):
    stock: float
    allocated: float
    unallocated: float
    demand: float
    unmet: float
    fulfillment: float
    spoilage: float
    spoilageValue: float
    remaining: float
    revenue: float
    acquisition: float
    soldAcquisition: float
    spoilageWriteoff: float
    remainingInventoryValue: float
    markdownAllocated: float
    fixedTransport: float
    variableTransport: float
    handling: float
    packaging: float | None
    storage: float | None
    platform: float | None
    tax: float | None
    disposal: float
    net: float

class Plan(Model):
    allocations: list[Allocation]
    metrics: Metrics
    unallocated: list[dict]
    unmet: list[dict]
    violations: list[str]
    strategy: str

class Result(Model):
    proposed: Plan
    baseline: Plan
    earliestExpiryBaseline: Plan
    rejected: list[dict]
    discounts: list[dict]
    objective: Objective
    explanation: str
    candidatesChecked: int
    guardrail: str
    binding: list[str]
