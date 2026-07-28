"""Alter Ego Shell 服務。"""
from app.services.shells.shell_formatter import build_shell_output, count_hashtags
from app.services.shells.shell_manager import ShellManager, ShellRule, get_shell_manager

__all__ = [
    "ShellManager",
    "ShellRule",
    "get_shell_manager",
    "build_shell_output",
    "count_hashtags",
]
