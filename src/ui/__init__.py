"""User interface package."""

__all__ = ["ModernMainWindow"]


def __getattr__(name):
    if name == "ModernMainWindow":
        from .app_ui import ModernMainWindow

        return ModernMainWindow
    raise AttributeError(name)
