from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class FormulaBase(BaseModel):
    formula_string: str
    description: str

class FormulaCreate(FormulaBase):
    pass

class Formula(FormulaBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

class CalculateRequest(BaseModel):
    formula: str

class PlotRequest(BaseModel):
    function: str
    x_min: float = -10.0
    x_max: float = 10.0