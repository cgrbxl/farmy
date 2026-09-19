"""Optional summary formatting. Queries are owned and supplied by each service."""
from .http import utc


def summarize(service, metrics, dependencies):
    with service.db() as db:
        db.execute('BEGIN')  # One internally consistent snapshot of this service only.
        counts = [{'label': label, 'value': db.execute(sql).fetchone()[0]} for label, sql in metrics]
        activity = [{'at': row[0], 'event': row[1], 'outcome': row[2]} for row in
                    db.execute('SELECT time,event,outcome FROM audit ORDER BY id DESC LIMIT 6')]
    return {'instanceId': service.config['identity'], 'observedAt': utc(),
            'counts': counts, 'activity': activity, 'dependencies': list(dependencies)}
