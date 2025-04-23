from logging import LoggerAdapter


class SeparatorAdapter(LoggerAdapter):
    """
    Logger adapter for separate logs.

    The adapter allows you to separate logs by unique IDs.
    """
    def process(self, msg, kwargs):
        kwargs.setdefault("extra", {}).update(self.extra)
        modified_msg: str = " | ".join((msg, f"[unique_id - {self.extra['unique_id']}"))
        return modified_msg, kwargs
