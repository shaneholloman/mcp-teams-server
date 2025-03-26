# MCP Teams Server

An MCP (Model Context Protocol) server implementation for Microsoft Teams integration, providing tools for managing Teams channels, threads, and messages through MCP.

## Features

- Start threads in channel with title and contents
- Update existing threads with messages
- Mention users in threads
- Read thread replies
- List channel team members

## Prerequisites

- uv package manager
- Python 3.10
- Microsoft Teams account with appropriate permissions

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd mcp-teams-server
```
2. Create a virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## Teams configuration

### Azure Bot registration

Follow the instructions provided by Microsoft regarding [this topic](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration?view=azure-bot-service-4.0&tabs=userassigned)

TODO: describe required resources: Azure Bot registration, Application registration, Client Credentials

### Microsoft application publishing

Create an application for Microsoft Teams using [Teams Developer Portal](https://learn.microsoft.com/en-us/microsoftteams/platform/concepts/build-and-test/teams-developer-portal).

You will need bot information from previous [Azure Bot Registration](#azure-bot-registration).

A sample application skeleton with required permissions and configuration is provided as [a model](./app/manifest.json)

## Usage

Start server:
```bash
uv run mcp-teams-server
```

## Development

TODO: add documentation

```bash
uv run pytest
```

### Build docker image

```bash
docker build . -t inditextech/mcp-teams-server
```

### Run interactively docker image

```bash
docker run -it inditextech/mcp-teams-server
```

### Setup Claude desktop to use docker image

```yaml
{
    "mcpServers": {
       "teams": {
            "command": "docker",
            "args": [
                "run",
                "-i"
                "--rm"
                "inditextech/mcp-teams-server"
            ],
            "env": {
                "TEAMS_APP_ID": "",
                "TEAMS_APP_PASSWORD": "",
                "TEAMS_APP_TYPE": "",
                "TEAMS_APP_TENANT_ID": "",
                "TEAM_ID": "",
                "TEAMS_CHANNEL_ID": "",
                "GRAPH_CLIENT_ID": "",
                "GRAPH_CLIENT_SECRET": "",
                "DOCKER_HOST": "unix:///var/run/docker.sock"
            }
        }
    }
}
```

### Setup Cline to use docker image

```yaml 
{
  "mcpServers": {
    "github.com/inditextech/mcp-teams-server/tree/main": {
      "command": "wsl",
      "args": [
        "TEAMS_APP_ID=",
        "TEAMS_APP_PASSWORD=",
        "TEAMS_APP_TYPE=",
        "TEAMS_APP_TENANT_ID=",
        "TEAM_ID=",
        "TEAMS_CHANNEL_ID=",
        "GRAPH_CLIENT_ID=",
        "GRAPH_CLIENT_SECRET=",
        "docker",
        "run",
        "-i",
        "--rm",
        "-e",
        "SLACK_BOT_TOKEN",
        "-e",
        "SLACK_TEAM_ID",
        "mcp/slack"
      ],
      "env": {
        "DOCKER_HOST": "unix:///var/run/docker.sock"
      },
      "disabled": false,
      "autoApprove": [],
      "timeout": 300
    }
  }
}
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security

For security concerns, please see our [Security Policy](SECURITY.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.



