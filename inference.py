import json

def predict(input_data):
    emails = input_data.get("emails", [])

    if not emails:
        return {"action_type": "submit"}

    email = emails[0]
    subject = email.get("subject", "").lower()

    if "urgent" in subject:
        return {
            "action_type": "classify",
            "email_id": email["id"],
            "label": "Urgent"
        }

    return {"action_type": "submit"}


if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    print(json.dumps(predict(data)))
