"""
Script to initialize a bot instance and send all possible locale messages to a specific user.

This script is used for testing purposes to verify that all locale messages are correctly
formatted and can be sent to a user. It initializes a bot instance and sends all possible
locale messages to the specified user ID.

Usage:
    python -m chathub_bot.tests.send_all_locale_messages

Environment variables:
    TG_BOT_TOKEN: Telegram bot token
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, TG_BOT_POSTGRES_USER, TG_BOT_POSTGRES_PASSWORD: PostgreSQL credentials
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VIRTUAL_HOST, TG_BOT_RABBITMQ_EXCHANGE, TG_BOT_RABBITMQ_QUEUE,
    TG_BOT_RABBITMQ_USERNAME, TG_BOT_RABBITMQ_PASSWORD: RabbitMQ settings
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_BUCKET: AWS credentials
"""

import asyncio
import json
import os
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Import from the bot package
from bot import TG_TOKEN, BotCommands, setup_logger
from bot.bot import DatingBot

# Set up logger
LOGGER = setup_logger(__name__)

# Target user ID
TARGET_USER_ID = 5356971580

async def send_all_locale_messages():
    """
    Initialize a bot instance and send all possible locale messages to the specified user ID.
    """
    LOGGER.info(f"Initializing bot to send all locale messages to user ID: {TARGET_USER_ID}")

    # Initialize the bot with default properties
    default_properties = DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN_V2
    )

    # Create the bot instance
    bot = DatingBot(tg_token=TG_TOKEN, default=default_properties, debug=True)

    try:
        # Connect to required services
        LOGGER.info("Connecting to required services...")
        loop = asyncio.get_running_loop()
        await bot.pg.connect(custom_loop=loop)
        await bot.rmq.connect(custom_loop=loop)

        # Send a starting message
        await bot.send_message(
            chat_id=TARGET_USER_ID,
            text="Starting to send all locale messages for testing purposes...",
            parse_mode=ParseMode.MARKDOWN_V2
        )

        # Send all command-based messages
        LOGGER.info("Sending command-based messages...")

        # 1. Request event registration confirmation
        try:
            await bot.request_event_registration_confirmation({"event_id": "1"}, TARGET_USER_ID)
        except Exception as e:
            LOGGER.error(f"Error sending registration confirmation: {e}")

        # 2. Send pre-event rules
        await bot.send_pre_event_rules(TARGET_USER_ID)

        # 3. Send meeting invitation
        meeting_data = {BotCommands.INVITE_TO_MEETING.value: {"url": "https://example.com/meeting"}}
        await bot.send_meeting_invitation(json.dumps(meeting_data), {"user_id": TARGET_USER_ID})

        # 4. Send partner rating request
        rating_data = {BotCommands.SEND_PARTNER_RATING_REQUEST.value: {"partner_id": "12345"}}
        await bot.send_partner_rating_request(json.dumps(rating_data), {"user_id": TARGET_USER_ID, "event_id": "1"})

        # 5. Send final dating message
        await bot.send_final_dating_message("", {"user_id": TARGET_USER_ID})

        # 6. Send break message
        await bot.send_break_message("", {"user_id": TARGET_USER_ID})

        # 7. Send ready for event request
        await bot.send_ready_for_event_request("", {"user_id": TARGET_USER_ID, "event_id": "1"})

        # 8. Send will take part in event message
        await bot.send_will_take_part_in_event_message("", {"user_id": TARGET_USER_ID})

        # 9. Send will not take part in event message
        await bot.send_will_not_take_part_in_event_message("", {"user_id": TARGET_USER_ID})

        # Send a completion message
        await bot.send_message(
            chat_id=TARGET_USER_ID,
            text="All locale messages have been sent successfully!",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    except Exception as e:
        LOGGER.error(f"Error sending messages: {e}")
    finally:
        # Close connections
        LOGGER.info("Closing connections...")
        await bot.pg.close()
        await bot.rmq.close()
        await bot.session.close()

if __name__ == "__main__":
    """
    Main entry point for the script.
    """
    LOGGER.info("Starting script to send all locale messages...")
    asyncio.run(send_all_locale_messages())
    LOGGER.info("Script completed.")
