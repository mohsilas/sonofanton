<div align="center"><h1>🤖 SonOfAnton (SOA) 🤖</h1></div>

<br>
<div align="center">
  <img/ src="https://github.com/user-attachments/assets/b7ca8b8b-7840-4b1d-aa40-c081e15d3af2" height="25">&nbsp;&nbsp;
  <img/ src="https://github.com/user-attachments/assets/69c67088-dcaf-4074-aa70-8fc42cb5f018" height="25">&nbsp;&nbsp;
  <img/ src="https://github.com/user-attachments/assets/3cd1ab55-deda-4cdd-a21e-951d91bf3231" height="25">&nbsp;&nbsp;
  <img/ src="https://github.com/user-attachments/assets/aaac5885-8d01-4b17-a778-e67a6d98d74b" height="25">
</div>
<br>

> A lightweight AI agent that monitors emails for instructions and executes tasks on your server. Built with Claude and Pushover integration for seamless task automation and notifications.

## ✨ Features

- 📧 Email monitoring with secure admin code verification
- 🧠 Powered by Claude's AI for natural language task interpretation
- 📱 Push notifications via Pushover for task status updates
- 📝 Blog management with automated Git deployment
- 🛠️ Extensible tool system for custom functions using Anthropic's tools format

## 🏹 Current Use Cases

- Automated blog updates with Markdown support
- Remote script execution on Linode servers
- Task status monitoring via push notifications

## 🧱 Setup Requirements

- Python 3.x
- Anthropic API key (for Claude)
- Pushover account (for notifications)
- Gmail account with App Password
- GitHub CLI (for blog deployment)

## 🛠️ Configuration

Initialize the SOA service with your credentials:

```python
soa = SOAService(
    "your-email@gmail.com",
    "your-app-password",
    'SUBJECT "your-admin-code"',
    "your-anthropic-api-key",
    "your-pushover-app-token",
    "your-pushover-user-key"
)
```

## ⚓ Adding Custom Tools

SOA uses Anthropic's tool calling format. To add new functions, update `tools.json` with your function schema. Pro tip: Feed your `tools.json` to an AI assistant to easily generate schemas for new functions. Example tool definition:

```json
{
  "name": "notification_send",
  "description": "Send a notification with optional title and priority",
  "input_schema": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The notification message content"
      },
      "title": {
        "type": "string",
        "description": "Optional notification title"
      }
    },
    "required": ["message"]
  }
}
```

## 🎠 Usage

1. Set up your credentials in main.py
2. Run the main loop:
   ```bash
   python main.py
   ```
3. Send an email with your admin code in the subject line
4. SOA will process your instructions and send notifications about the results

## 🎫 License
This project falls under the [GNU general public license.](https://github.com/mohsilas/clipycards/blob/main/LICENSE)
