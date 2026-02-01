import os
import logging
import random
from datetime import datetime
from typing import Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot states
DEPOSIT, WITHDRAW = range(2)

# Store bot state per user
user_states: Dict[int, bool] = {}  # True = trading active, False = trading stopped

def generate_eth_address():
    """Generate a random ETH-like address"""
    chars = '0123456789abcdef'
    return '0x' + ''.join(random.choice(chars) for _ in range(40))

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with buttons"""
    welcome_text = """
🤖 *Welcome to ETH Trading Bot*

*Features:*
• Deposit ETH to start trading
• Automated ETH market trading
• Real-time profit tracking
• Secure withdrawals

*Commands:*
/start - Show this menu
/deposit - Deposit ETH
/withdraw - Withdraw ETH
/status - Check bot status
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data="deposit"),
            InlineKeyboardButton("📈 Trade", callback_data="trade")
        ],
        [
            InlineKeyboardButton("⏸️ Stop/Start", callback_data="toggle_trade"),
            InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="status")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "deposit":
        # Generate deposit address
        eth_address = generate_eth_address()
        response = f"""
💎 *DEPOSIT ETH*

Send ETH to this address:
`{eth_address}`

*Minimum deposit:* 0.1 ETH
*Network:* Ethereum ERC-20
*Confirmation required:* 12 blocks

⚠️ *Important:*
• Only send ETH to this address
• Do not send other tokens
• Contact support if deposit doesn't appear within 30 minutes
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ I've Deposited", callback_data="check_deposit")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif query.data == "trade":
        # Simulate trading action
        trade_id = random.randint(100000, 999999)
        response = f"""
🚀 *TRADE EXECUTED*

*Trade ID:* #{trade_id}
*Market:* ETH/USDT
*Position:* Long
*Leverage:* 5x
*Entry Price:* ${random.randint(1800, 2500)}
*Stop Loss:* -2%
*Take Profit:* +5%

✅ *Status:* Position opened successfully!
⏱️ *Time:* {datetime.now().strftime('%H:%M:%S')}

Hurry! I'm going into the ETH market now to make profit for you! 📈
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 View Positions", callback_data="positions")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif query.data == "toggle_trade":
        # Toggle trading state
        current_state = user_states.get(user_id, False)
        user_states[user_id] = not current_state
        
        if user_states[user_id]:
            response = "✅ *TRADING STARTED*\n\nTrading bot is now active and monitoring the ETH market!"
        else:
            response = "⏸️ *TRADING STOPPED*\n\nAll positions are closed. Trading bot is now inactive."
        
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif query.data == "withdraw":
        response = """
💸 *WITHDRAW ETH*

Please send your ETH address where you want to receive funds.

*Minimum withdrawal:* 0.05 ETH
*Network fee:* 0.001 ETH

Enter your ETH address:
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown'
        )
        return WITHDRAW
    
    elif query.data == "status":
        # Check bot and trading status
        trading_status = "ACTIVE ✅" if user_states.get(user_id, False) else "STOPPED ⏸️"
        response = f"""
📊 *BOT STATUS*

*Trading Status:* {trading_status}
*Total Trades Today:* {random.randint(5, 20)}
*Win Rate:* {random.randint(65, 85)}%
*Current Balance:* {random.uniform(1.5, 5.0):.2f} ETH
*Estimated Profit:* {random.uniform(0.1, 2.5):.2f} ETH

*Last Update:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="status")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif query.data == "back":
        # Return to main menu
        await start(update, context)
    
    elif query.data == "check_deposit":
        # Simulate deposit check
        response = f"""
🔄 *CHECKING DEPOSIT...*

✅ Deposit confirmed!
📍 *Transaction ID:* 0x{random.getrandbits(256):064x}
💰 *Amount:* {random.uniform(0.5, 3.0):.2f} ETH
📅 *Time:* {datetime.now().strftime('%H:%M:%S')}

Your funds are now available for trading!
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📈 Start Trading", callback_data="trade")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif query.data == "positions":
        # Show open positions
        response = f"""
📈 *OPEN POSITIONS*

1. *ETH/USDT Long*
   • Size: {random.uniform(0.5, 2.0):.2f} ETH
   • P&L: +{random.uniform(0.01, 0.5):.3f} ETH
   • Time: {datetime.now().strftime('%H:%M')}

2. *ETH/BTC Short*
   • Size: {random.uniform(0.1, 1.0):.2f} BTC
   • P&L: -{random.uniform(0.001, 0.05):.4f} BTC
   • Time: {datetime.now().strftime('%H:%M')}

*Total Unrealized P&L:* +{random.uniform(0.01, 0.8):.3f} ETH
"""
        await query.edit_message_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="positions")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )

async def handle_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle withdrawal address input"""
    eth_address = update.message.text
    
    # Simple validation
    if not eth_address.startswith("0x") or len(eth_address) != 42:
        await update.message.reply_text(
            "❌ Invalid ETH address. Please enter a valid Ethereum address starting with 0x:"
        )
        return WITHDRAW
    
    # Simulate withdrawal
    response = f"""
🎉 *WITHDRAWAL REQUESTED*

✅ Withdrawal processed successfully!

📍 *To Address:* `{eth_address}`
💰 *Amount:* 10.25 ETH
📤 *Network:* Ethereum Mainnet
⏱️ *ETA:* 5-15 minutes
📋 *TX ID:* 0x{random.getrandbits(256):064x}

Congratulations! 10 ETH profit is coming your way! 🚀

*Note:* Includes 0.25 ETH trading profit from today's session.
"""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Check Status", callback_data="status")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="back")]
    ])
    
    await update.message.reply_text(
        response,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text(
        "Operation cancelled.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back")]
        ])
    )
    return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Start the bot"""
    # Get token from environment variable
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create Application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler for withdrawal
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern='^withdraw$')],
        states={
            WITHDRAW: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_withdraw)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    # Start the Bot
    PORT = int(os.environ.get('PORT', 8443))
    
    if os.environ.get('RENDER'):
        # Running on Render
        webhook_url = os.environ.get('RENDER_EXTERNAL_URL')
        if webhook_url:
            application.run_webhook(
                listen="0.0.0.0",
                port=PORT,
                url_path=TOKEN,
                webhook_url=f"{webhook_url}/{TOKEN}"
            )
    else:
        # Running locally with polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
