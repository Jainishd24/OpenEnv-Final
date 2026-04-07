import json
import sys

def predict(input_data):
    emails = input_data.get("emails", [])

    if not emails:
        return {"action_type": "submit"}

    email = emails[0]
    subject = email.get("subject", "").lower()

    if "urgent" in subject:
        return {
            "action_type": "classify",
            "email_id": email.get("id", ""),
            "label": "Urgent"
        }

    return {"action_type": "submit"}


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read().strip()

        # ✅ handle empty input
        if not raw_input:
            data = {}
        else:
            data = json.loads(raw_input)

        result = predict(data)
        print(json.dumps(result))

    except Exception:
        # ✅ NEVER crash (critical for OpenEnv)
        print(json.dumps({"action_type": "submit"}))
