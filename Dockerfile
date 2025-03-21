FROM ghcr.io/astral-sh/uv:python3.13-alpine

ENV TEAMS_APP_ID=""
ENV TEAMS_APP_PASSWORD="",
ENV TEAMS_APP_TYPE="",
ENV TEAMS_APP_TENANT_ID="",
ENV TEAM_ID="",
ENV TEAMS_CHANNEL_ID="",
ENV GRAPH_CLIENT_ID="",
ENV GRAPH_CLIENT_SECRET=""

ADD . /app
WORKDIR /app
RUN uv sync --frozen

CMD ["uv", "run", "mcp-teams-server"]