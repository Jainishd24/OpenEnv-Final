from models import Email, TaskContext, Action, Observation, Reward, Info, State
from tasks import get_task_setup, get_grader

class EmailTriageEnv:
    def __init__(self):
        self.current_state: State = None
        self.grader = None
        self.steps = 0

    def reset(self, difficulty: str = "easy") -> Observation:
        emails, context = get_task_setup(difficulty)
        self.grader = get_grader(difficulty)
        self.steps = 0
        
        obs = Observation(
            emails=emails,
            task_context=context,
            last_action_feedback="Environment reset.",
            scheduled_meetings=[]
        )
        self.current_state = State(
            observation=obs,
            reward=Reward(score=0.0, message="Task started."),
            done=False,
            info=Info(steps_taken=0, metrics={})
        )
        return obs

    def step(self, action: Action) -> tuple[Observation, Reward, bool, Info]:
        if self.current_state is None or self.current_state.done:
            raise ValueError("Environment must be reset or is already done.")
            
        self.steps += 1
        feedback = ""
        obs = self.current_state.observation

        if action.action_type == "view_email":
            email = next((e for e in obs.emails if e.id == action.email_id), None)
            if email:
                feedback = f"Viewed email {email.id}."
            else:
                feedback = f"Email {action.email_id} not found."
                
        elif action.action_type == "classify":
            email = next((e for e in obs.emails if e.id == action.email_id), None)
            if email:
                email.label = action.label
                feedback = f"Labeled email {email.id} as '{action.label}'."
            else:
                feedback = f"Email {action.email_id} not found to classify."
                
        elif action.action_type == "reply":
            email = next((e for e in obs.emails if e.id == action.email_id), None)
            if email:
                email.replied = True
                email.reply_content = action.content
                feedback = f"Replied to email {email.id}."
            else:
                feedback = f"Email {action.email_id} not found to reply."
                
        elif action.action_type == "move_to_folder":
            email = next((e for e in obs.emails if e.id == action.email_id), None)
            if email:
                email.folder = action.folder_name
                feedback = f"Moved email {email.id} to folder '{action.folder_name}'."
            else:
                feedback = f"Email {action.email_id} not found to move."
                
        elif action.action_type == "schedule_meeting":
            meeting_details = action.content or "Meeting scheduled"
            obs.scheduled_meetings.append(meeting_details)
            feedback = f"Scheduled meeting: {meeting_details}"

        elif action.action_type == "submit":
            feedback = "Task submitted by agent."
            self.current_state.done = True

        else:
            feedback = f"Unknown action type: {action.action_type}"

        obs.last_action_feedback = feedback
        
        # Calculate partial/final reward dynamically
        reward = self.grader(self.current_state)
        
        # Update Info
        info = Info(steps_taken=self.steps, metrics={})

        self.current_state.observation = obs
        self.current_state.reward = reward
        self.current_state.info = info

        return obs, reward, self.current_state.done, info

    def state(self) -> State:
        return self.current_state
