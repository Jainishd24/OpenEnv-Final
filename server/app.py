from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/reset")
def reset():
    return {
        "observation": {
            "emails": [],
            "task_context": {}
        }
    }

@app.post("/step")
def step():
    return {
        "observation": {
            "emails": [],
            "task_context": {},
            "last_action_feedback": "ok"
        },
        "reward": {"score": 1},
        "done": True
    }

# 🔥 REQUIRED MAIN FUNCTION
def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

# 🔥 REQUIRED ENTRYPOINT
if __name__ == "__main__":
    main()
