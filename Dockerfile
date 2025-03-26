FROM ghcr.io/astral-sh/uv:python3.10-alpine

# ENV TEAMS_APP_ID="" TEAMS_APP_PASSWORD="" TEAMS_APP_TYPE="" TEAMS_APP_TENANT_ID="" TEAM_ID="" TEAMS_CHANNEL_ID=""

ADD . /app
WORKDIR /app
RUN uv sync --frozen

CMD ["uv", "run", "mcp-teams-server"]