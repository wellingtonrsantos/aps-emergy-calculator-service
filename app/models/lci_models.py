from pydantic import BaseModel


class LCIProduct(BaseModel):
    id: int
    name: str
    description: str


class LCIFlow(BaseModel):
    flow_name: str
    amount: float
    unit: str
    flow_direction: str
    uev: float
    category: str
