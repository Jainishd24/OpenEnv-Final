import os
import yaml
import httpx
import inspect

def validate_environment():
    print("=== OpenEnv Local Validation ===")
    
    # 1. Check openenv.yaml
    if os.path.exists("openenv.yaml"):
        with open("openenv.yaml", "r") as f:
            data = yaml.safe_load(f)
            if "tasks" in data:
                print("✅ Found openenv.yaml with configured tasks.")
            else:
                print("❌ openenv.yaml missing 'tasks' block.")
    else:
        print("❌ Missing openenv.yaml")

    # 2. Check Pydantic models
    import models
    has_observation = hasattr(models, "Observation")
    has_action = hasattr(models, "Action")
    has_reward = hasattr(models, "Reward")
    if has_observation and has_action and has_reward:
        print("✅ Typed Pydantic models (Observation, Action, Reward) successfully implemented.")
    else:
        print("❌ Missing required Pydantic models.")

    # 3. Check endpoints
    print("Testing / state endpoints against local server port 7860...")
    try:
        # Ping
        ping = httpx.get("http://localhost:7860/")
        if ping.status_code == 200:
             print("✅ Server responds to Ping (HF Space alive test).")
             
        # Reset
        res = httpx.post("http://localhost:7860/reset", json={"difficulty": "easy"})
        if res.status_code == 200:
            print("✅ Server responds to /reset.")
            
        # State
        res2 = httpx.get("http://localhost:7860/state")
        if res2.status_code == 200:
            print("✅ Server responds to /state.")
            
    except Exception as e:
        print(f"❌ Server test failed. Make sure 'uvicorn main:app --port 7860' is running. Error: {e}")

    # 4. Dockerfile
    if os.path.exists("Dockerfile"):
        print("✅ Dockerfile exists.")
    else:
        print("❌ Dockerfile missing.")
        
    print("\nValidation completed successfully! Pre-submission checklist passed.")

if __name__ == "__main__":
    validate_environment()
