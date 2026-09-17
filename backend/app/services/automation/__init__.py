"""
自動化服務模組（延遲匯出，避免 import 鏈拉起 config／pydantic）。
"""

__all__ = [
    "TopicCollector",
    "AutomationWorkflow",
    "SchedulerService",
]


def __getattr__(name: str):
    if name == "TopicCollector":
        from app.services.automation.topic_collector import TopicCollector
        return TopicCollector
    if name == "AutomationWorkflow":
        from app.services.automation.workflow import AutomationWorkflow
        return AutomationWorkflow
    if name == "SchedulerService":
        from app.services.automation.scheduler import SchedulerService
        return SchedulerService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
