# BlitzSSH - SSH Cracking Tool

## Description
BlitzSSH is a powerful and efficient SSH login brute-force testing tool. It allows security professionals to test SSH credentials from an input file and identify valid login combinations.

It supports multiple credential formats, making it versatile for different list structures.

## Features
- Supports various credential formats:
  - `hostname:username:password`
  - `hostname:port:username:password`
  - `hostname;user;password`
  - `user:password:hostname:port`
  - `user;password;hostname`
  - `user:port:password:hostname`
- Multi-threaded execution for faster results
- Automatic logging of valid and invalid SSH credentials
- Telegram integration for real-time notifications of successful logins
- Beautifully formatted output using `rich` and `pystyle`

## Dependencies
Ensure you have the following Python packages installed:
```bash
pip install paramiko python-telegram-bot rich pystyle
```

## Usage
1. Clone the repository:
```bash
git clone https://github.com/HackfutSec/BlitzSSH.git
cd BlitzSSH
```

2. Edit the script to add your Telegram bot token and chat ID:
```python
TELEGRAM_BOT_TOKEN = "your_bot_token"
TELEGRAM_CHAT_ID = "your_chat_id"
```

3. Run the script:
```bash
python blitzssh.py
```

4. Enter the path to your credential list when prompted.

## Output
- **Good_Ssh.txt**: Contains valid SSH credentials
- **Bad_Ssh.txt**: Contains invalid login attempts
- Successful logins are sent to Telegram if configured

## Important Notes
- Do **not** use this tool for unauthorized access. It is intended for security research and penetration testing only.
- Ensure you have permission before testing any systems.

## Disclaimer
BlitzSSH is provided for educational purposes. The authors are not responsible for any misuse of this tool.

## Author
**HackFutSec** - Ethical Hacking & Security Research
