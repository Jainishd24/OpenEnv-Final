from models import Email, TaskContext, State, Reward
from typing import List, Tuple

def get_task_setup(difficulty: str) -> Tuple[List[Email], TaskContext]:
    if difficulty == "easy":
        emails = [
            Email(
                id="e1",
                sender="prince@nigeria.xyz",
                subject="URGENT: Claim your inheritance",
                body="You have won 10,000,000. Send me your bank details."
            )
        ]
        context = TaskContext(
            task_id="task_easy_1",
            difficulty="easy",
            goal="Classify the email in the inbox.",
            rules=["If the email is a scam, label it as 'Spam'.", "When finished, use the 'submit' action."]
        )
        return emails, context

    elif difficulty == "medium":
        emails = [
            Email(
                id="e2",
                sender="angry_customer@domain.com",
                subject="My order is completely broken!",
                body="I just received order #449 and it is shattered. I demand a fix immediately!"
            )
        ]
        context = TaskContext(
            task_id="task_medium_1",
            difficulty="medium",
            goal="Resolve the customer complaint.",
            rules=[
                "Reply to the customer with an apology and offer a 'refund'.",
                "Label the email as 'Resolved'.",
                "When finished, use the 'submit' action."
            ]
        )
        return emails, context

    elif difficulty == "hard":
        emails = [
            Email(id="e3", sender="newsletter@tech.com", subject="Daily Tech News", body="Here is your news..."),
            Email(id="e4", sender="promo@store.com", subject="50% off!", body="Buy now..."),
            Email(id="e5", sender="vip@enterprise.com", subject="Enterprise Deal", body="We want to upgrade to enterprise. Can we schedule a meeting with sales?")
        ]
        context = TaskContext(
            task_id="task_hard_1",
            difficulty="hard",
            goal="Triage the inbox completely and handle VIP requests.",
            rules=[
                "Move newsletters and promos to the 'archives' folder.",
                "Move the enterprise deal email to the 'urgent' folder.",
                "Schedule a meeting containing the word 'sales'.",
                "When finished, use the 'submit' action."
            ]
        )
        return emails, context
    else:
        raise ValueError(f"Unknown difficulty: {difficulty}")

def grade_easy(state: State) -> Reward:
    email = next((e for e in state.observation.emails if e.id == "e1"), None)
    if email and email.label and email.label.lower() == "spam":
        return Reward(score=1.0, message="Correctly classified the email as Spam.")
    return Reward(score=0.0, message="Email was not classified as Spam.")

def grade_medium(state: State) -> Reward:
    email = next((e for e in state.observation.emails if e.id == "e2"), None)
    if not email:
        return Reward(score=0.0, message="Target email not found.")
    
    score = 0.0
    messages = []
    
    if email.label and email.label.lower() == "resolved":
        score += 0.5
        messages.append("Labeled as Resolved.")
    else:
        messages.append("Not labeled as Resolved.")
        
    if email.replied and email.reply_content:
        content_lower = email.reply_content.lower()
        if "refund" in content_lower and ("sorry" in content_lower or "apologize" in content_lower):
            score += 0.5
            messages.append("Polite reply with a refund offer sent.")
        elif "refund" in content_lower:
            score += 0.25
            messages.append("Refund offered, but missing apology.")
        else:
            messages.append("Reply sent but missing refund offer.")
    else:
        messages.append("No reply sent.")
        
    return Reward(score=score, message=" ".join(messages))

def grade_hard(state: State) -> Reward:
    score = 0.0
    messages = []
    
    emails = {e.id: e for e in state.observation.emails}
    
    # 0.4 total available for archiving
    archived_correctly = sum([1 for eid in ["e3", "e4"] if eid in emails and emails[eid].folder.lower() == "archives"])
    if archived_correctly == 2:
        score += 0.4
        messages.append("Moved promos/newsletters to archives.")
    else:
        messages.append(f"Moved {archived_correctly}/2 to archives.")
        
    # 0.2 total for urgent routing
    if "e5" in emails and emails["e5"].folder.lower() == "urgent":
        score += 0.2
        messages.append("Moved enterprise deal to urgent.")
    else:
        messages.append("Failed to move enterprise deal to urgent.")
        
    # 0.4 for scheduling meeting
    scheduled = any("sales" in meeting.lower() for meeting in state.observation.scheduled_meetings)
    if scheduled:
        score += 0.4
        messages.append("Scheduled a meeting with sales.")
    else:
        messages.append("Failed to schedule a meeting with sales.")
        
    return Reward(score=round(score, 2), message=" ".join(messages))

def get_grader(difficulty: str):
    if difficulty == "easy":
        return grade_easy
    elif difficulty == "medium":
        return grade_medium
    elif difficulty == "hard":
        return grade_hard
    raise ValueError(f"Unknown difficulty: {difficulty}")

