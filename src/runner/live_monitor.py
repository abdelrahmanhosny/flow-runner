import rethinkdb as r
from django.conf import settings


class LiveMonitor:
    def __init__(self, flow_id):
        self.flow_id = flow_id
        self.logs = ''
        self.conn = r.connect(settings.LIVE_MONITORING_URL, password=settings.LIVE_MONITORING_PASSWORD)
        r.db('openroad').table('flow_log').insert({'openroad_uuid': flow_id,'logs': self.logs}).run(self.conn)

    
    def append(self, logs):
        self.logs += logs
        r.db('openroad').table('flow_log').filter(r.row['openroad_uuid'] == self.flow_id).update({'logs': self.logs}).run(self.conn)

    def close(self):
        self.conn.close()