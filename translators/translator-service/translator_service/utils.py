import importlib.metadata


def load_plugins():
    """Auto-discover installed plugins."""
    return {
        ep.name: ep.load()
        for ep in importlib.metadata.entry_points(group="translator_service.plugins")
    }