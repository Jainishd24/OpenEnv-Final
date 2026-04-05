import httpx

def test_env():
    print("Testing /reset")
    res = httpx.post("http://localhost:7860/reset", json={"difficulty": "medium"})
    res.raise_for_status()
    obs = res.json()
    print("Obs emails count:", len(obs["emails"]))
    
    # Take an action
    action = {
        "action_type": "reply",
        "email_id": "e2",
        "content": "We apologize for the inconvenience. We've issued a refund."
    }
    
    print(f"Taking action: {action}")
    res = httpx.post("http://localhost:7860/step", json=action)
    res.raise_for_status()
    data = res.json()
    print("Reward score (should be 0.5 or so for reply with refund):", data["reward"]["score"])
    
    # Try classifying
    action = {
        "action_type": "classify",
        "email_id": "e2",
        "label": "Resolved"
    }
    print(f"Taking action: {action}")
    res = httpx.post("http://localhost:7860/step", json=action)
    res.raise_for_status()
    data = res.json()
    print("Reward score after resolving (should be higher):", data["reward"]["score"])
    print("Message:", data["reward"]["message"])
    
if __name__ == "__main__":
    test_env()
