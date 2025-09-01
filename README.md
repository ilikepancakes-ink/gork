# Gork Bot

This is the Gork Bot, a Discord bot with various functionalities.

## Features

### Message Logging
The bot logs user messages and bot responses to a SQLite database for conversation history and statistics.

### User Settings
Users can configure personal settings such as NSFW mode and content filter levels.

### Steam Account Linking
Users can link their Discord accounts to their Steam accounts. This allows the bot to retrieve Steam-related information and enables future Steam-integrated features.

**How to Link Your Steam Account:**
(Instructions will be added here once the bot commands are implemented)

## Database Schema

The bot uses a SQLite database (`data/bot_messages.db`) with the following tables:

### `messages`
Stores logged user messages.

### `responses`
Stores bot responses linked to original user messages.

### `user_settings`
Stores individual user preferences and linked external accounts.
- `user_id` (TEXT, UNIQUE, NOT NULL): Discord user ID.
- `username` (TEXT): Discord username.
- `user_display_name` (TEXT): Discord display name.
- `nsfw_mode` (BOOLEAN, DEFAULT FALSE): User's NSFW content preference.
- `content_filter_level` (TEXT, DEFAULT 'strict'): User's content filter setting.
- `steam_id` (TEXT): Linked Steam 64-bit ID.
- `steam_username` (TEXT): Linked Steam username.
- `steam_linked_at` (DATETIME): Timestamp when the Steam account was linked.
- `created_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP): Timestamp of record creation.
- `updated_at` (DATETIME, DEFAULT CURRENT_TIMESTAMP): Timestamp of last record update.

### `guild_settings`
Stores server-specific settings.

### `channel_settings`
Stores channel-specific settings.

## Setup and Installation
(Instructions will be added here)

## Usage
(Instructions will be added here)

## Development
(Instructions will be added here)