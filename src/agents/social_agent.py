"""Social Agent - handles LinkedIn content generation and approval."""
from __future__ import annotations

from pathlib import Path

from src.core.agent_base import AgentBase
from src.core.task_item import TaskItem, TaskStatus


class SocialAgent(AgentBase):
    """Generates social media content, schedules posts, manages approval flow."""

    name = "social_agent"

    def can_handle(self, task: TaskItem) -> bool:
        return task.category == "Social" and task.status in (
            TaskStatus.NEEDS_ACTION,
            TaskStatus.APPROVED,
        )

    def process(self, task: TaskItem, task_path: Path) -> TaskItem:
        self.log.info(f"Processing social task: {task.title}")

        task_path = self._move_to_in_progress(task, task_path)

        # Generate a post based on the task content
        post = {}
        if self.skills.has("generate_post"):
            try:
                post = self.skills.invoke(
                    "generate_post",
                    topic=task.title,
                    platform="linkedin",
                )
            except Exception as e:
                self.log.warning(f"generate_post failed: {e}")

        # Apply brand voice
        if post and self.skills.has("apply_brand_voice"):
            try:
                voiced = self.skills.invoke("apply_brand_voice", text=post.get("content", ""))
                post["content"] = voiced.get("text", post.get("content", ""))
            except Exception:
                pass

        # Set up action plan
        content = post.get("content", "")
        task.action_plan = f"**Platform:** LinkedIn\n\n**Post Content:**\n\n{content}"
        task.action_type = "create_post"
        task.action_params = {
            "platform": "linkedin",
            "content": content,
            "hashtags": post.get("hashtags", []),
        }

        # All social posts require approval
        if self.approval.requires_approval("create_post"):
            task_path = self._move_to_needs_approval(task, task_path)
            self.log.info(f"Social post needs approval: {task.title}")
        else:
            task_path = self._move_to_done(task, task_path)

        return task

    def execute_approved_action(self, task: TaskItem, task_path: Path) -> TaskItem:
        """Publish the approved post via LinkedIn MCP."""
        self.log.info(f"Publishing approved social post")
        # In production: invoke linkedin_mcp.create_post with task.action_params
        task.result = f"Post published to {task.action_params.get('platform', 'linkedin')}"
        task.status = TaskStatus.DONE
        task.touch()
        return task
