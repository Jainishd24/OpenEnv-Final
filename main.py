from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from models import Action, Observation, Reward, Info, State
from env import EmailTriageEnv

app = FastAPI(title="Email Triage OpenEnv")

# Instantiate a global environment state for this server instance
# (Note: In a true multi-agent production setup, you'd use session IDs.
# For standard OpenEnv interface, single-instance state is typical per deployed container.)
environment = EmailTriageEnv()

class ResetRequest(BaseModel):
    difficulty: str = "easy"

class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Info

@app.get("/")
def ping():
    return {"status": "ok"}

@app.post("/reset", response_model=Observation)
def reset(request: Optional[ResetRequest] = None):
    diff = request.difficulty if request else "easy"
    try:
        return environment.reset(difficulty=diff)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResponse)
def step(action: Action):
    if environment.current_state is None:
        raise HTTPException(status_code=400, detail="Environment must be reset first.")
    
    try:
        obs, reward, done, info = environment.step(action)
        return StepResponse(
            observation=obs,
            reward=reward,
            done=done,
            info=info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=State)
def get_state():
    if environment.current_state is None:
        raise HTTPException(status_code=400, detail="Environment hasn't been initialized with /reset yet.")
    return environment.state()

