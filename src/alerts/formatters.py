from .alert_engine import AlertEngine
from ..models.alert import Alert


def format_alert_box(alert: Alert) -> str:
    severity_symbols = {
        "INFO": "[INFO]",
        "WARNING": "[WARNING]",
        "CRITICAL": "[CRITICAL ALERT]"
    }
    symbol = severity_symbols.get(alert.severity.value, "[ALERT]")
    lines = [
        f"\n+-------------------------------------------------------------+",
        f"| {symbol} - {alert.category.value} (Tick {alert.tick})",
        f"+-------------------------------------------------------------+",
        f"| Title  : {alert.title}",
        f"| Source : {alert.source_entity_id}",
        f"| Details: {alert.message}",
        f"+-------------------------------------------------------------+"
    ]
    return "\n".join(lines)
