HIGH = "High"
MEDIUM = "Medium"
LOW = "Low"


def get_severity_score(severity: str) -> int:
    """
    Convert severity text into numeric score.
    Useful later for sorting issues.
    """

    severity_scores = {
        HIGH: 3,
        MEDIUM: 2,
        LOW: 1
    }

    return severity_scores.get(severity, 0)