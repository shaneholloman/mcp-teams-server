import os
from dataclasses import dataclass

@dataclass
class BotConfiguration:
    def __init__(self):
        self.APP_ID = os.environ.get("TEAMS_APP_ID", "")
        self.APP_PASSWORD = os.environ.get("TEAMS_APP_PASSWORD", "")
        self.APP_TYPE = os.environ.get("TEAMS_APP_TYPE", "SingleTenant")
        self.APP_TENANTID = os.environ.get("TEAMS_APP_TENANT_ID", "")
        self.TEAM_ID = os.environ.get("TEAM_ID", "")
        self.TEAMS_CHANNEL_ID = os.environ.get("TEAMS_CHANNEL_ID", "")
        self.GRAPH_CLIENT_ID = os.environ.get("GRAPH_CLIENT_ID", "")
        self.GRAPH_CLIENT_SECRET = os.environ.get("GRAPH_CLIENT_SECRET", "")