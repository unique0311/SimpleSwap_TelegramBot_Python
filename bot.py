import os
from dotenv import load_dotenv
# import threading
# import schedule
import time
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    CallbackQueryHandler, 
    MessageHandler,
    ConversationHandler,
    filters,
)

from simpleswapapi import SimpleSwap
from text import *

CHOOSE_ORIGINAL_CURRENCY = "CHOOSE_ORIGINAL_CURRENCY"
INPUT_RECIPIENT_ADDRESS = "INPUT_RECIPIENT_ADDRESS"
CHOOSE_TARGET_CURRENCY = "CHOOSE_TARGET_CURRENCY"
CHANGE_SENDER_ADDRESS = "CHANGE_SENDER_ADDRESS"
INPUT_REFUND_ADDRESS = "INPUT_REFUND_ADDRESS"
INPUT_AMOUNT = "INPUT_AMOUNT"
GET_RESULT = "GET_RESULT"
EXCHANGE = "EXCHANGE"
CONFIRM = "CONFIRM"
STATUS = "STATUS"
CANCEL = "CANCEL"
DONE = "DONE"
FIXED = "false"

END = ConversationHandler.END

# Load the .env file
load_dotenv()

# Access the token
BOT_TOKEN = os.environ.get('BOT_TOKEN')

class SimpleSwapBot:
    swap_api = SimpleSwap()

    def __init__(self):
        self.app = ApplicationBuilder().token(BOT_TOKEN).build()
        self.from_currency = ""
        self.to_currency = ""
        self.stop_invoking = False

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        context.user_data['from_currency'] = None
        context.user_data['to_currency'] = None
        context.user_data['amount'] = None
        context.user_data['recipient_address'] = None

        text = start_text()
        await update.message.reply_text(text=text, parse_mode='HTML')

    async def _send_message(self, chat_id, text, reply_markup="", disable_preview=False):
        result = await self.app.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=disable_preview,
                parse_mode='HTML'
            )
        return result
    
    async def _edit_message(self, chat_id, message_id, text, reply_markup="", disable_preview=False):
        result = await self.app.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            disable_web_page_preview=disable_preview,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return result

    def get_text_by_symbol(self, symbol):
        networks = {
            "usdterc20": "USDT",
            "usdc": "USDC",
            "btc": "BTC",
            "eth": "ETH",
            "sol": "SOL",
            "ltc": "LTC",
            "xmr": "XMR",
            "xrp": "XRP",
            "maticerc20": "MATIC",
        }
        return networks.get(symbol)

    def get_currencies_markup(self):
        keyboard = [
            [
                InlineKeyboardButton("USDT", callback_data="usdterc20"),
                InlineKeyboardButton("USDC", callback_data="usdc"),
                InlineKeyboardButton("BTC", callback_data="btc"),
                InlineKeyboardButton("ETH", callback_data="eth"),
                InlineKeyboardButton("SOL", callback_data="sol"),
            ],
            [
                InlineKeyboardButton("LTC", callback_data="ltc"),
                InlineKeyboardButton("XMR", callback_data="xmr"),
                InlineKeyboardButton("XRP", callback_data="xrp"),
                InlineKeyboardButton("MATIC", callback_data="maticerc20")
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        return markup
    
    def cancel_button(self):
        cancel_button = [InlineKeyboardButton(text="CANCEL", callback_data="CANCEL_CONV")]
        keyboard = []
        keyboard.append(cancel_button)
        return InlineKeyboardMarkup(keyboard)
        
    
    def filter_markUp(self, markup, callback_data):
        first_line = list(markup.inline_keyboard[0])
        second_line = list(markup.inline_keyboard[1])

        keyboard = []

        for button in first_line:
            if button.callback_data == callback_data:
                first_line.remove(button)

        for button in second_line:
            if button.callback_data == callback_data:
                second_line.remove(button)
        
        keyboard.append(first_line)
        keyboard.append(second_line)

        return InlineKeyboardMarkup(keyboard)

    async def select_from_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        
        markup = self.get_currencies_markup()
        message = await self._send_message(chat_id, text=wait_text())

        text = from_currency_text()
        await self._edit_message(chat_id, message.message_id, text, markup)
        return CHOOSE_TARGET_CURRENCY

    async def select_to_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = update.effective_chat.id

        message = await self._send_message(chat_id, text=wait_text())

        if "CANCEL" in query.data:
            await self._send_message(chat_id, cancel_text())
            return END

        # await self.monitor_exchange(123, chat_id)

        context.user_data['from_currency'] = self.swap_api.get_currency(query.data)
        context.user_data['from_currency']['text'] = self.get_text_by_symbol(query.data)

        text = to_currency_text()
        markup = self.get_currencies_markup()
        updated_markup = self.filter_markUp(markup, query.data)

        await self._edit_message(chat_id, message.message_id, text, updated_markup)
        return INPUT_AMOUNT

    async def input_amount(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        chat_id = update.effective_chat.id
        
        message = await self._send_message(chat_id, text=wait_text())
        
        if "CANCEL" in query.data:
            await self._send_message(chat_id, cancel_text())
            return END
        
        context.user_data['to_currency'] = self.swap_api.get_currency(query.data)
        context.user_data['to_currency']['text'] = self.get_text_by_symbol(query.data)

        from_currency = context.user_data['from_currency']
        to_currency = context.user_data['to_currency']

        result = self.swap_api.get_ranges(FIXED, from_currency, to_currency)
        text = amount_text(context.user_data, result['min'], result['max'])
        
        await self._edit_message(chat_id, message.message_id, text)
        return INPUT_RECIPIENT_ADDRESS

    async def input_recipient_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        amount = update.message.text
        chat_id = update.effective_chat.id
        
        context.user_data['amount'] = amount
        from_currency = context.user_data['from_currency']['symbol']
        to_currency = context.user_data['to_currency']['symbol']

        if not "refund_address" in context.user_data:
            estimated_amount = self.swap_api.get_estimated(FIXED, from_currency, to_currency, amount)
            context.user_data['estimated_amount'] = estimated_amount
            text = refund_prompt_text(context.user_data)
            await self._send_message(chat_id, text)
            return INPUT_REFUND_ADDRESS
        else:
            is_available = self.swap_api.check_exchanges(FIXED, from_currency, to_currency, amount)

            if is_available:
                estimated_amount = self.swap_api.get_estimated(FIXED, from_currency, to_currency, amount)
                context.user_data['estimated_amount'] = estimated_amount
                text = recipient_address_text(context.user_data)
                
                await self._send_message(chat_id, text)
                return CONFIRM
            else:
                text = invalid_amount_text()

                await self._send_message(chat_id, text)
                return INPUT_RECIPIENT_ADDRESS
    
    async def input_refund_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        address = update.message.text

        message = await self._send_message(chat_id, text=wait_text())

        if not "refund_address" in context.user_data:
            context.user_data['refund_address'] = address
            text = refund_address_prompt(address)
            await self._edit_message(chat_id, message.message_id, text)
            return INPUT_REFUND_ADDRESS
        else:
            context.user_data['recipient_address'] = address
            text = confirm_text(context.user_data)
            keyboard = [
                [
                    InlineKeyboardButton("Exchange", callback_data="EXCHANGE"),
                ],
                [
                    InlineKeyboardButton("Cancel", callback_data="CANCEL"),
                ]
            ]
            markup = InlineKeyboardMarkup(keyboard)
            await self._edit_message(chat_id, message.message_id, text, markup)
            return DONE
        
    async def confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        address = update.message.text

        context.user_data['recipient_address'] = address
        message = await self._send_message(chat_id, text=wait_text())
        text = confirm_text(context.user_data)
        keyboard = [
            [
                InlineKeyboardButton("Exchange", callback_data="EXCHANGE"),
            ],
            [
                InlineKeyboardButton("Cancel", callback_data="CANCEL"),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await self._edit_message(chat_id, message.message_id, text, markup)
        return DONE
    
    async def done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        command = query.data
        chat_id = update.effective_chat.id

        message = await self._send_message(chat_id, text=wait_text())
        
        from_currency = context.user_data['from_currency']['symbol']
        to_currency = context.user_data['to_currency']['symbol']
        amount = context.user_data['amount']
        recipient_address = context.user_data['recipient_address']
        refund_address = context.user_data['refund_address']
        data = {
            "fixed": FIXED,
            "currency_from": from_currency,
            "currency_to": to_currency,
            "amount": amount,
            "address_to": recipient_address,
            "extra_id_to": "",
            "user_refund_address": refund_address,
            "user_refund_extra_id": "string"
        }

        if EXCHANGE in command:
            result = self.swap_api.create_exchanges(data)

            print(result)

            if "code" in result and result["code"]:
                text = address_failed()
                await self._edit_message(chat_id, message.message_id, text)
                return END
            else:
                text = deposit_text(context.user_data, result['address_from'], result['id'])
                await self._edit_message(chat_id, message.message_id, text)

                await self.monitor_exchange(exchange_id=result['id'], chat_id=chat_id)

            return GET_RESULT
        elif CANCEL in command:
            text = cancel_text()
            await self._edit_message(chat_id, message.message_id, text)
            return END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        context.user_data['from_currency'] = None
        context.user_data['to_currency'] = None
        context.user_data['amount'] = None
        context.user_data['recipient_address'] = None

        await update.message.reply_text("Bye! Please type <em>/wash</em>, when you want my help.", parse_mode='HTML')
        return END
        
    async def result(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(text="Please input exchange ID:")
        return STATUS

    async def get_exchange(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        exchange_id = update.message.text

        result = self.swap_api.get_exchange(exchange_id)
        if result:
            await update.message.reply_text(text=f"Your transaction status is <code>{result['status']}</code>", parse_mode="HTML")
        else:
            await update.message.reply_text(text="There is no transaction you are looking for!")

        return GET_RESULT
    
    async def setting(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        text = input_sender_address()

        await self._send_message(chat_id, text)
        return CHANGE_SENDER_ADDRESS
    
    async def change_sender_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        sender_address = update.message.text
        context.user_data['refund_address'] = sender_address
        text = set_refund_address(sender_address)

        await self._send_message(chat_id, text)
        return END

    async def monitor_exchange(self, exchange_id, chat_id):
        self.stop_invoking = False
        while not self.stop_invoking:
            await self.check_exchange(exchange_id)
            time.sleep(60)

        await self._send_message(chat_id, "Your swap has been completed! Thank you for using Wash Bot.")

    async def check_exchange(self, exchange_id):
        print("monitor_exchange")
        result = self.swap_api.get_exchange(exchange_id)
        if result and result['status'] == "finished":
            self.stop_invoking = True
        else:
            self.stop_invoking = False
        
    def run(self):
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("wash", self.select_from_currency)],
            states={
                CHOOSE_TARGET_CURRENCY: [CallbackQueryHandler(self.select_to_currency)],
                INPUT_AMOUNT: [CallbackQueryHandler(self.input_amount)],
                INPUT_RECIPIENT_ADDRESS: [MessageHandler(filters.TEXT & filters.Regex(r'^\d+(\.\d+)?$'), self.input_recipient_address)],
                INPUT_REFUND_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_refund_address)],
                CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.confirm)],
                DONE: [CallbackQueryHandler(self.done)],
                GET_RESULT: [CommandHandler("result", self.result)],
                STATUS: [MessageHandler(filters.TEXT, self.get_exchange)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel),
                CommandHandler("wash", self.select_from_currency)
            ],
        ))
        self.app.add_handler(ConversationHandler(
            entry_points=[CommandHandler("refund", self.setting)],
            states={
                CHANGE_SENDER_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.change_sender_address)],
            },
            fallbacks=[
                
            ],
            
        ))
        self.app.run_polling()
