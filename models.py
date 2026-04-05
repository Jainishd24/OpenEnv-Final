from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class Email(BaseModel):
    id: str = Field(description="Unique identifier for the email.")
    sender: str = Field(description="Email address of the sender.")
    subject: str = Field(description="Subject line of the email.")
    body: str = Field(description="Content of the email.")
    folder: str = Field(default="inbox", description="The folder where the email is currently located.")
    label: Optional[str] = Field(default=None, description="Assigned label (e.g., 'Spam', 'Important').")
    replied: bool = Field(default=False, description="Whether a reply has been sent.")
    reply_content: Optional[str] = Field(default=None, description="The content of the sent reply.")

class TaskContext(BaseModel):
    task_id: str = Field(description="Unique identifier for the active task.")
    difficulty: Literal["easy", "medium", "hard"] = Field(description="Task difficulty level.")
    goal: str = Field(description="The primary objective the agent must achieve.")
    rules: List[str] = Field(description="Rules and constraints the agent must follow.")

class Action(BaseModel):
    action_type: Literal["view_email", "classify", "reply", "move_to_folder", "schedule_meeting", "submit"] = Field(
        description="The type of action to perform. To end the task and submit, use 'submit'."
    )
    email_id: Optional[str] = Field(default=None, description="ID of the email to interact with.")
    label: Optional[str] = Field(default=None, description="Label to apply (used with 'classify').")
    content: Optional[str] = Field(default=None, description="Content of the reply or meeting details (used with 'reply' and 'schedule_meeting').")
    folder_name: Optional[str] = Field(default=None, description="Destination folder name (used with 'move_to_folder').")

class Observation(BaseModel):
    emails: List[Email] = Field(description="List of emails currently accessible to the agent.")
    task_context: TaskContext = Field(description="Context and instructions for the current task.")
    last_action_feedback: str = Field(description="Feedback from the last action performed.")
    scheduled_meetings: List[str] = Field(default=[], description="List of meetings scheduled.")

class Reward(BaseModel):
    score: float = Field(ge=0.0, le=1.0, description="Reward score from 0.0 to 1.0.")
    message: str = Field(description="Reasoning or description for the assigned reward.")

class Info(BaseModel):
    steps_taken: int = Field(default=0, description="Number of steps taken in the current episode.")
    metrics: dict = Field(default_factory=dict, description="Additional evaluation metrics.")

class State(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: Info
