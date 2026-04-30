"""Project-wide constants."""

APP_NAME = "Operations RCA NLP"
APP_FULL_NAME = "Operations Root Cause Analytics with NLP"
APP_SUBTITLE = (
    "Natural Language Processing for Incident Narrative Analysis and "
    "Root Cause Factor Classification"
)
APP_VERSION = "0.1.0"
DEFAULT_DOMAIN = "aviation"
DEFAULT_THRESHOLD = 0.50
DEFAULT_TOP_K = 5
MAX_TOP_K = 22

LIMITATION_NOTE = (
    "Outputs are root-cause-related factor indicators for analyst decision support "
    "and do not establish definitive causality."
)

DOMAIN_PLACEHOLDERS = [
    {
        "domain_id": "maintenance_work_orders",
        "display_name": "Maintenance Work Orders",
        "status": "planned",
        "description": (
            "Planned domain for contributory-factor classification in maintenance "
            "narratives."
        ),
    },
    {
        "domain_id": "asset_failure_logs",
        "display_name": "Asset Failure Narratives",
        "status": "planned",
        "description": (
            "Planned domain for anomaly-factor classification in asset failure logs."
        ),
    },
    {
        "domain_id": "service_disruption_reports",
        "display_name": "Service Disruption Reports",
        "status": "planned",
        "description": (
            "Planned domain for operational incident narrative analysis in service "
            "disruptions."
        ),
    },
]
