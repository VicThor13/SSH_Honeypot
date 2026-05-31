# Autonomous DevSecOps SSH Honeypot

A lightweight, secure SSH Honeypot written in Python using `paramiko`. This tool simulates a fake SSH server on port `2222`, permanently rejects all authentication attempts, and logs the attacker's source IP, username, and password by sending real-time alerts to a Discord webhook. 

## Features

- **Port 2222 Listener**: Simulates an SSH service to attract unauthorized access attempts.
- **Zero Authentication**: Always returns `AUTH_FAILED` to guarantee no one can actually connect to the honeypot.
- **Discord Integration**: Real-time alerts via Webhooks with the attacker's credentials.
- **Multi-threading**: Can handle multiple concurrent connection attempts simultaneously.
- **Secure Docker Environment**: Runs as a non-root user within a minimal Alpine Linux container.

## Proof of Concept / Screenshot

<!-- 📸 INSERT YOUR SCREENSHOT HERE -->
![Discord Alert Proof](URL_TO_YOUR_SCREENSHOT_HERE.png)
*(Screenshot of the Discord Webhook alert showing the captured IP, Username, and Password)*

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine)
- A Discord Server with Webhook capabilities.

## Setup & Deployment

1. **Navigate to the project folder**.

2. **Build the Docker Image**:
   ```bash
   docker build -t ssh-honeypot .
   ```

3. **Run the Container**:
   Replace the `DISCORD_WEBHOOK_URL` value with your actual Discord Webhook URL.
   ```bash
   docker run -d -p 2222:2222 -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN" --name my-honeypot ssh-honeypot
   ```

## Testing the Honeypot

From another machine (or a new terminal), try to SSH into the honeypot:
```bash
ssh root@localhost -p 2222
```
Enter any random password. The connection will be rejected, and you will instantly receive an alert on Discord with the tested credentials!

## Disclaimer

This project is intended for defensive security monitoring, threat intelligence, and educational purposes only. Do not deploy honeypots on networks where you do not have explicit authorization.
