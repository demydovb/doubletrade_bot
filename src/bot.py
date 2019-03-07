import os
import asyncio
import logging
import telegram
import re
import itertools

from functools import wraps
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler
from telegram.ext.dispatcher import run_async

from skyscanner import SkyScannerInterface

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LIST_OF_ADMINS = [449915551, 488295339]
CHOOSING, AIRPORT_PROCESSING, LINK_PROCESSING, DONE = range(4)
HIDE_KEYBOARD = telegram.ReplyKeyboardRemove()
CUSTOM_KEYBOARD = telegram.ReplyKeyboardMarkup([['Add Airport', 'Generate Links']], resize_keyboard=True)
BITLY_TOKEN = 'db26b02e2c8a614f719abb2b93206e1e77a133d0'

SOURCES = {
    'SITE':"https://clk.tradedoubler.com/click?p=232108&a=2937217&g=21113908&url=http://",
    'TG':"https://clk.tradedoubler.com/click?p=232108&a=3068494&g=21113908&url=http://",
    'FB':"https://clk.tradedoubler.com/click?p=232108&a=3068495&g=21113908&url=http://",
}


def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            logger.error(msg="Unauthorized access denied for {}.".format(user_id))
            bot.sendMessage(chat_id=update.message.chat_id, text="Unauthorized access denied.")
            return
        return func(bot, update, *args, **kwargs)

    return wrapped


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Welcome!")


@run_async
@restricted
def start_generate_links(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Select action",
                     reply_markup=CUSTOM_KEYBOARD)
    logger.info(msg="User {} starting generate links.".format(update.effective_user.id))
    return CHOOSING


def collect_links(bot, update, user_data):
    text = update.message.text
    if text.lower() in ('end', 'done'):
        return done(bot, update, user_data)

    links = user_data.setdefault('links', [])
    links.append(text[9:])
    bot.send_message(chat_id=update.message.chat_id, text="That's it?")

    return LINK_PROCESSING


def start_collect_links(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Please, start sending links. Send *end* or *done* when you're ready to get output.",
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=HIDE_KEYBOARD)

    return LINK_PROCESSING


def start_add_airport_to_db(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="""Send airport IATA code and city name in next format:\n\n
    *IATA_CODE:CITY_NAME*""",
                     parse_mode=telegram.ParseMode.MARKDOWN,
                     reply_markup=HIDE_KEYBOARD)
    return AIRPORT_PROCESSING


def add_airport_to_db(bot, update):
    text = update.message.text
    logger.info(msg="User {} adding new airport to DB...".format(update.effective_user.id))
    if not re.match(r"^\w+:\w+$", text):
        logger.error(msg="User {} send data with wrong format ".format(update.effective_user.id))
        update.message.reply_text("Please, send IATA code and city name in right format")
        return AIRPORT_PROCESSING
    update.message.reply_text(
        "Done!\n\n Please, start sending links. Send *end* or *done* when you're ready to get output.",
        parse_mode=telegram.ParseMode.MARKDOWN)
    logger.info(msg="User {} added new airport to DB.".format(update.effective_user.id))
    return LINK_PROCESSING


def done(bot, update, user_data):
    try:
        if not user_data:
            update.message.reply_text(text="Your did not send me any links")
        else:
            update.message.reply_text(text="Your affiliates links are being generated, please wait...")
            logger.info("Urls for user {} are being generated".format(update.effective_user.id))
            links = user_data['links']
            skyscanner = SkyScannerInterface(BITLY_TOKEN, SOURCES, links)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(skyscanner.main())
            answer_to_user = ''
            for url in itertools.chain.from_iterable(result):
                answer_to_user+= url + '\n'
            update.message.reply_text(text=answer_to_user)
            user_data.clear()
    except:
        logger.info("User {} sent wrong data".format(update.effective_user.id))
        update.message.reply_text(text="You sent wrong data!")
    finally:
        logger.info("Urls for user {} successfully generated".format(update.effective_user.id))
        return ConversationHandler.END


def unknown(bot, update):
    update.message.reply_text(text="Sorry, I didn't understand that command.")


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start_generate_links', start_generate_links)],

    states={
        CHOOSING: [RegexHandler('^Generate Links$',
                                start_collect_links,
                                ),
                   RegexHandler('^Add Airport$',
                                start_add_airport_to_db),
                   ],
        LINK_PROCESSING: [MessageHandler(Filters.text,
                                         collect_links,
                                         pass_user_data=True
                                         ),
                          ],
        AIRPORT_PROCESSING: [
                             MessageHandler(Filters.text,
                                            add_airport_to_db,
                                            ),
                             ],
    },

    fallbacks=[CommandHandler('done', done, pass_user_data=True)]
)


if __name__ == "__main__":

    updater = Updater(token=os.getenv('TELEGRAM_BOT_TOKEN'))

    start_command = CommandHandler('start', start)
    unknown_command = MessageHandler(Filters.command | Filters.text, unknown)

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(start_command)
    updater.dispatcher.add_handler(unknown_command)

    logger.info("Starting bot...")
    updater.start_polling()
