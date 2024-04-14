from common.log import logger
from bot.service import generate_random_numbers, save_to_excel
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

EAN_NUMBER = range(2)


async def start_ean(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about the number of EAN codes to generate."""
    await update.message.reply_text(
        "Hi! My name is Gef Bot. I will hold a conversation with you. "
        "Send /cancel_ean to stop talking to me.\n\n"
        "How many EAN codes do you want to generate?"
    )

    return EAN_NUMBER


async def ean_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the number of EAN codes to generate and ends the conversation."""
    try:
        ean_code_quantity = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Please enter a valid number.")
        return EAN_NUMBER

    random_numbers_list = generate_random_numbers(ean_code_quantity)
    save_to_excel(random_numbers_list)

    await update.message.reply_text(
        f"{ean_code_quantity} EAN codes have been generated and stored in an ean_codes.xlsx."
    )
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open("./excel-files/ean/ean_codes.xlsx", "rb"),
    )
    return ConversationHandler.END


async def cancel_ean(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Bye! I hope we can talk again some day.")

    return ConversationHandler.END


ean_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start_ean", start_ean)],
    states={
        EAN_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ean_number)],
    },
    fallbacks=[CommandHandler("cancel_ean", cancel_ean)],
)
