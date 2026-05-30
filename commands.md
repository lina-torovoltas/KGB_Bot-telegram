# 0xNULL-Bot Commands

## Pre-setup Files

These files must exist in the root directory before running the bot:
- `quotes.txt` - Database for quotes (one quote per line)
- `users.txt` - List of monitored user IDs (one ID per line)

## Automated Features

The bot performs the following tasks automatically:
- Monitors text messages from users listed in `users.txt`
- Scans every word for blacklisted or swear content
- Instantly deletes the message if a match is found


## User Commands

```text
/quote          - Sends a random quote wrapped in markdown code formatting.
/uptime         - Displays the bot's precise running time (days, hours, minutes).
/ask <question> - Queries the bot's learned database for a response.
```

### Teaching Example
```text
/teach Question=Answer
```
*The "=" sign is strictly required to split the question and the answer.*

## Admin Commands
```text
/add_user <user_id>    - Adds a numerical Telegram ID to the monitoring list.
/remove_user <user_id> - Removes a numerical Telegram ID from the monitoring list.
```
*Restricted to chat administrators only, requires a numerical user ID.*

Examples:
```text
/add_user 123123123
/remove_user 123123123
```

***
Developed by Lina Torovoltas — © 2025-2026 All rights reserved.
