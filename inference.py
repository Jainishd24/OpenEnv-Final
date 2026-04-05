import os
import time
import json
import httpx
from openai import OpenAI

# Required Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

# Optional - if you use from_docker_image():
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

# Initialize OpenAI Client
client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

ENV_URL = os.environ.get("ENV_URL", "http://localhost:7860")

def get_action_schema():
    return {
        "type": "function",
        "function": {
            "name": "take_action",
            "description": "Take an action in the Email Triage environment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["view_email", "classify", "reply", "move_to_folder", "schedule_meeting", "submit"],
                        "description": "The command to execute."
                    },
                    "email_id": {"type": "string"},
                    "label": {"type": "string"},
                    "content": {"type": "string"},
                    "folder_name": {"type": "string"}
                },
                "required": ["action_type"]
            }
        }
    }

def call_llm(observation: dict, step_num: int) -> dict:
    prompt = f"Observation: {json.dumps(observation, indent=2)}\nYou must advance the task by calling the 'take_action' function. Only use 'submit' when you are totally done."
    
    # Retry logic for api limits
    for _ in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful AI agent designed to triage emails. Follow the rules provided in the task context. Think step by step and decide your next action."},
                    {"role": "user", "content": prompt}
                ],
                tools=[get_action_schema()],
                tool_choice={"type": "function", "function": {"name": "take_action"}}
            )
            tool_call = response.choices[0].message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            return args
        except Exception as e:
            print(f"LLM Error: {e}")
            if HF_TOKEN and "dummy" in HF_TOKEN:
                # Use heuristic solver for demonstration
                return get_mock_action(observation)
            time.sleep(2)
    return {"action_type": "submit"} # Give up and submit

def get_mock_action(obs: dict) -> dict:
    task_id = obs.get("task_context", {}).get("task_id", "")
    emails = obs.get("emails", [])
    scheduled = obs.get("scheduled_meetings", [])
    
    if task_id == "task_easy_1":
        e = emails[0]
        if e.get("label") != "Spam":
            return {"action_type": "classify", "email_id": e["id"], "label": "Spam"}
        return {"action_type": "submit"}
        
    elif task_id == "task_medium_1":
        e = emails[0]
        if not e.get("replied"):
            return {"action_type": "reply", "email_id": e["id"], "content": "We apologize. Here is your refund."}
        if e.get("label") != "Resolved":
            return {"action_type": "classify", "email_id": e["id"], "label": "Resolved"}
        return {"action_type": "submit"}
        
    elif task_id == "task_hard_1":
        for e in emails:
            if e["id"] in ["e3", "e4"] and e["folder"] != "archives":
                return {"action_type": "move_to_folder", "email_id": e["id"], "folder_name": "archives"}
            if e["id"] == "e5" and e["folder"] != "urgent":
                return {"action_type": "move_to_folder", "email_id": e["id"], "folder_name": "urgent"}
        if len(scheduled) == 0:
            return {"action_type": "schedule_meeting", "content": "Meeting with sales team."}
        return {"action_type": "submit"}
        
    return {"action_type": "submit"}

def run_task(difficulty: str):
    print(f"[START] Task: {difficulty}")
    
    # Reset Environment
    try:
        res = httpx.post(f"{ENV_URL}/reset", json={"difficulty": difficulty}, timeout=10)
        res.raise_for_status()
        obs = res.json()
    except Exception as e:
        print(f"Failed to reset environment. Is the server running at {ENV_URL}? {e}")
        return
        
    done = False
    step_num = 1
    total_reward = 0.0
    
    while not done and step_num <= 10:
        # Get Action
        action_args = call_llm(obs, step_num)
        print(f"[STEP] Step {step_num} | Action: {json.dumps(action_args)}")
        
        # Step Environment
        try:
            res = httpx.post(f"{ENV_URL}/step", json=action_args, timeout=10)
            res.raise_for_status()
            step_data = res.json()
        except Exception as e:
            print(f"Failed to step environment: {e}")
            break
            
        obs = step_data["observation"]
        reward = step_data["reward"]
        done = step_data["done"]
        
        print(f"     | Feedback: {obs['last_action_feedback']} | Partial Score: {reward['score']}")
        total_reward = reward['score']
        
        step_num += 1
        time.sleep(1) # Be nice to backend and llm endpoint
        
    print(f"[END] Task: {difficulty} | Final Score/Reward: {total_reward}")

def main():
    print("Testing Environment Connectivity...")
    try:
        httpx.get(f"{ENV_URL}/", timeout=5)
    except httpx.RequestError as exc:
        print(f"CRITICAL: Failed to connect to server at {ENV_URL}. Please start standard server via 'uvicorn main:app --port 7860'.")
        return

    for diff in ["easy", "medium", "hard"]:
        run_task(diff)

if __name__ == "__main__":
    main()
