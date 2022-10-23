import requests

from telegram import Update, ParseMode
from telegram.utils.helpers import mention_html
from telegram.error import BadRequest
from telegram.ext import (
    CallbackContext,
    Filters,
    MessageHandler,
)

from Shikimori import dispatcher
from Shikimori.vars import DEMONS, DRAGONS, LOG_CHANNEL
from Shikimori.modules.sql import global_bans_sql as sql
from Shikimori.modules.helper_funcs.misc import send_to_list

def phoenix(update: Update, context: CallbackContext):
    msg = update.effective_message
    user = msg.from_user
    bot = context.bot
    
    URL = f'https://sheltered-taiga-39139.herokuapp.com/check/{user.id}'
    result = requests.get(URL).json()
    
    try:
        is_gban = bool(result['is_gban'])
    except:
        pass
    
    if is_gban:
        try:
            reason = str(result['reason'])
        except:
            reason = None
        sql.gban_user(user.id, user.username or user.first_name, reason)
        update.effective_message.reply_text(f"""
# SCANNED
User ID: {user.id}
Reason: {reason}
        """)
        log_message = (
        f"#GBANNED\n"
        f"<b>Originated from:</b> <code>Scanner</code>\n"
        f"<b>Banned User:</b> {mention_html(user.id, user.first_name)}\n"
        f"<b>Banned User ID:</b> <code>{user.id}</code>\n"
    )
        if LOG_CHANNEL:
            try:
                log = bot.send_message(LOG_CHANNEL, log_message, parse_mode=ParseMode.HTML)
            except BadRequest as excp:
                log = bot.send_message(
                    LOG_CHANNEL,
                    log_message
                    + "\n\nFormatting has been disabled due to an unexpected error.",
                )

        else:
            send_to_list(bot, DRAGONS + DEMONS, log_message, html=True)

dispatcher.add_handler(MessageHandler(Filters.all & Filters.chat_type.groups, phoenix, run_async = True))