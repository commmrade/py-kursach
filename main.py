import base64
import io
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sympy import sympify, SympifyError
import matplotlib.pyplot as plt
import numpy as np
from database import engine, Base, get_db
from schemas import UserCreate, Token, FormulaCreate, Formula, CalculateRequest, PlotRequest, UserLogin
from auth import get_password_hash, authenticate_user, create_access_token, get_current_user
from maths import create_formula, get_formulas, get_formula, update_formula, delete_formula
from models import User
from sqlalchemy import insert
from datetime import timedelta
from auth import ACCESS_TOKEN_EXPIRE_MINUTES
app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/register", summary="Register a new user")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await authenticate_user(db, user.username, user.password)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    
    stmt = insert(User).values(username=user.username, hashed_password=hashed_password)
    await db.execute(stmt)
    await db.commit()
    return {"msg": "User registered"}

@app.post("/login", response_model=Token, summary="Login to get access token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/formulas/", response_model=Formula, summary="Create a new formula")
async def create_formula_endpoint(formula: FormulaCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    formula_id = await create_formula(db, formula, current_user.id)
    return await get_formula(db, formula_id, current_user.id)

@app.get("/formulas/", response_model=List[Formula], summary="Get all formulas for the user")
async def read_formulas(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await get_formulas(db, current_user.id)

@app.get("/formulas/{formula_id}", response_model=Formula, summary="Get a specific formula")
async def read_formula(formula_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    formula = await get_formula(db, formula_id, current_user.id)
    if formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    return formula

@app.put("/formulas/{formula_id}", summary="Update a formula")
async def update_formula_endpoint(formula_id: int, formula: FormulaCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing_formula = await get_formula(db, formula_id, current_user.id)
    if existing_formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    await update_formula(db, formula_id, formula, current_user.id)
    return {"msg": "Formula updated"}

@app.delete("/formulas/{formula_id}", summary="Delete a formula")
async def delete_formula_endpoint(formula_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    existing_formula = await get_formula(db, formula_id, current_user.id)
    if existing_formula is None:
        raise HTTPException(status_code=404, detail="Formula not found")
    await delete_formula(db, formula_id, current_user.id)
    return {"msg": "Formula deleted"}

@app.post("/calculate/", summary="Calculate a mathematical formula")
async def calculate(request: CalculateRequest):
    try:
        result = sympify(request.formula)
        return {"result": str(result)}
    except SympifyError:
        raise HTTPException(status_code=422, detail="Invalid formula")

@app.post("/plot/", summary="Plot a function and return base64 image")
async def plot(request: PlotRequest):
    try:
        x = np.linspace(request.x_min, request.x_max, 400)
        y = [sympify(request.function).subs('x', val) for val in x]
        plt.figure()
        plt.plot(x, y)
        plt.title(f"Plot of {request.function}")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return {"image": img_base64}
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))