from datetime import datetime, timedelta

import pandas as pd


def generate_features_for_next_24h(self):
    """Generate naive time-based features for next 24h"""
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    future_times = [now + timedelta(hours=i) for i in range(24)]

    df = pd.DataFrame(
        {
            "hour": [t.hour for t in future_times],
            "day_of_week": [t.weekday() for t in future_times],
            "is_weekend": [t.weekday() >= 5 for t in future_times],
        }
    )

    return df
