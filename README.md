# Nyaa-bot-discord-RSS

Nyaa Bot RSS is a Discord bot written in Python to monitor RSS feeds and send updates to a specified Discord channel. The bot uses Docker for easy deployment and execution.

## Features

- Monitors specified RSS feeds for new content.
- Sends formatted notifications to a specific Discord channel.
- Logs activities and errors for easy debugging.

## Prerequisites

- **Docker** and **Docker Compose** installed on your machine.
- A Discord server and a bot configured with an authentication token.
- A `.env` file with configuration information.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/aruseus98/Nyaa-bot-discord-RSS.git
   cd Nyaa-bot-discord-RS
   ```

2. **Set up environment variables:**

Create a .env file from the .envEXAMPLE template and fill it with your information:

   ```
    DEBUG_MODE=true
    DISCORD_TOKEN=Your_Discord_Token
    DISCORD_CHANNEL_ID=Your_Discord_Channel_ID
   ```

3. **Build and start the Docker container:**

   ```bash
    docker-compose up --build -d
   ```

## Usage

- The bot will automatically connect to Discord and start monitoring the RSS feeds specified in urls/rss_urls.json.
- New entries from the RSS feeds will be sent to the configured Discord channel.

## Logging

- The bot's logs are saved in the logs directory when in debug mode.
- Group states and the last processed entries are stored in the state and last_entry directories.