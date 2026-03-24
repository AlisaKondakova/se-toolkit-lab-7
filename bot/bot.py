#!/usr/bin/env python3
import os
import sys
import logging
import re
import requests
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:42002")
BACKEND_API_KEY = os.getenv("BACKEND_API_KEY")

class IntentRouter:
    def __init__(self, backend_url, api_key):
        self.backend_url = backend_url
        self.api_key = api_key
    
    def _make_request(self, endpoint, params=None):
        """Make API request to backend"""
        url = f"{self.backend_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            if params:
                response = requests.get(url, headers=headers, params=params, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            logger.error(f"API error {response.status_code}: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None
    
    def _format_labs(self, items):
        """Format labs list"""
        labs = [item for item in items if item.get('type') == 'lab']
        if not labs:
            return "No labs found."
        result = "📚 *Available Labs:*\n\n"
        for lab in labs:
            lab_id = lab.get('id', '')
            lab_name = lab.get('name', lab.get('title', f'Lab {lab_id}'))
            result += f"• **{lab_id}** — {lab_name}\n"
        return result
    
    def _format_pass_rates(self, lab_id, data):
        """Format pass rates for a lab"""
        if not data:
            return f"No data available for {lab_id}"
        result = f"📊 *{lab_id} - Pass Rates*\n\n"
        total_rate = 0
        for task in data:
            task_name = task.get('task', task.get('name', 'Task'))
            pass_rate = task.get('pass_rate', task.get('rate', 0))
            attempts = task.get('attempts', 0)
            result += f"• {task_name}: {pass_rate:.1f}% ({attempts} attempts)\n"
            total_rate += pass_rate
        avg_rate = total_rate / len(data) if data else 0
        result += f"\n*Average: {avg_rate:.1f}%*"
        return result
    
    def _format_top_learners(self, lab_id, data, limit=5):
        """Format top learners"""
        if not data:
            return f"No top learner data for {lab_id}"
        result = f"🏆 *Top {limit} Learners in {lab_id}*\n\n"
        for i, learner in enumerate(data[:limit], 1):
            name = learner.get('name', learner.get('learner_id', f'Student {i}'))
            score = learner.get('score', 0)
            result += f"{i}. **{name}** — {score:.1f}%\n"
        return result
    
    def route(self, message):
        """Route user message to appropriate action"""
        message_lower = message.lower()
        
        # Greeting
        if re.search(r'\b(hi|hello|hey|greetings|hi there)\b', message_lower):
            return """👋 *Hello! I'm your Lab Analytics Assistant!*

I can help you with:
• 📋 Listing all available labs
• 📊 Showing scores and pass rates for any lab
• 🏆 Finding top learners
• 📉 Comparing pass rates across labs

*Try these examples:*
• "what labs are available?"
• "show me scores for lab 04"
• "which lab has the lowest pass rate?"
• "top learners in lab 03"

What would you like to know?"""
        
        # Help
        if re.search(r'\b(help|what can you do|capabilities)\b', message_lower):
            return """🤖 *I can help you with lab analytics!*

*Commands:*
• Ask about labs: "what labs are available?"
• Get scores: "show me scores for lab 04"
• Compare labs: "which lab has the lowest pass rate?"
• Top students: "top learners in lab 03"
• Group performance: "show groups for lab 03"

Just type your question in natural language!"""
        
        # List labs
        if re.search(r'(what|which).*(labs|tasks|available|do you have)', message_lower):
            data = self._make_request("/items/")
            if data:
                return self._format_labs(data)
            return "❌ Unable to fetch labs. Please check if the backend is running."
        
        # Get pass rates for a specific lab
        lab_match = re.search(r'lab[- ]?(\d+)', message_lower)
        if lab_match:
            lab_num = lab_match.group(1).zfill(2)
            lab_id = f"lab-{lab_num}"
            
            # If they ask for scores/pass rates
            if re.search(r'(score|pass|rate|result|performance|how.*doing)', message_lower):
                data = self._make_request("/analytics/pass-rates", params={"lab": lab_id})
                if data:
                    return self._format_pass_rates(lab_id, data)
                return f"❌ No data available for {lab_id}"
            
            # If they ask for top learners
            if re.search(r'(top|best|highest).*(learner|student)', message_lower):
                limit = 5
                data = self._make_request("/analytics/top-learners", params={"lab": lab_id, "limit": limit})
                if data:
                    return self._format_top_learners(lab_id, data, limit)
                return f"❌ No top learner data for {lab_id}"
            
            # If they ask for groups
            if re.search(r'(group|team)', message_lower):
                data = self._make_request("/analytics/groups", params={"lab": lab_id})
                if data:
                    result = f"👥 *Group Performance in {lab_id}*\n\n"
                    for group in data:
                        group_name = group.get('group', group.get('name', 'Group'))
                        score = group.get('score', 0)
                        students = group.get('students', 0)
                        result += f"• **{group_name}**: {score:.1f}% ({students} students)\n"
                    return result
                return f"❌ No group data for {lab_id}"
            
            # If they just mention a lab without specific question
            return f"📌 *What would you like to know about {lab_id}?*\n\n• Scores/pass rates\n• Top learners\n• Group performance\n\nJust ask me directly!"
        
        # Which lab has lowest pass rate?
        if re.search(r'(lowest|worst|minimum).*(pass|rate|result|performing)', message_lower):
            items = self._make_request("/items/")
            if items:
                labs = [item for item in items if item.get('type') == 'lab']
                results = []
                for lab in labs:
                    lab_id = lab.get('id')
                    data = self._make_request("/analytics/pass-rates", params={"lab": lab_id})
                    if data and len(data) > 0:
                        avg_rate = sum(t.get('pass_rate', t.get('rate', 0)) for t in data) / len(data)
                        results.append((lab_id, avg_rate))
                
                if results:
                    results.sort(key=lambda x: x[1])
                    result = "🔍 *Lab Pass Rate Comparison*\n\n"
                    for lab_id, rate in results:
                        indicator = " ⬇️ *LOWEST*" if lab_id == results[0][0] else ""
                        result += f"• {lab_id}: {rate:.1f}%{indicator}\n"
                    result += f"\n*Lowest pass rate: {results[0][0]}* at {results[0][1]:.1f}%"
                    return result
            return "❌ Unable to analyze pass rates across labs."
        
        # Top learners without specific lab
        if re.search(r'(top|best).*(learner|student)', message_lower):
            return "Which lab would you like to see top learners for?\n\nExample: *'top learners in lab 04'*"
        
        # Fallback
        return """🤔 *I'm not sure what you're asking.*

I can help you with:
• Listing labs: "what labs are available?"
• Lab scores: "show me scores for lab 04"
• Compare labs: "which lab has the lowest pass rate?"
• Top learners: "top students in lab 03"

Try rephrasing your question!"""

# Keyboard buttons
KEYBOARD = [
    [KeyboardButton("📋 What labs are available?")],
    [KeyboardButton("📊 Show scores for lab 04")],
    [KeyboardButton("🏆 Top learners in lab 04")],
    [KeyboardButton("📉 Which lab has lowest pass rate?")],
    [KeyboardButton("👥 Show groups for lab 03")],
    [KeyboardButton("❓ Help")]
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with keyboard"""
    reply_markup = ReplyKeyboardMarkup(KEYBOARD, resize_keyboard=True)
    await update.message.reply_text(
        "🤖 *Lab Analytics Bot*\n\n"
        "I can help you analyze lab performance data using natural language!\n\n"
        "Try asking me questions like:\n"
        "• 'What labs are available?'\n"
        "• 'Show me scores for lab 04'\n"
        "• 'Which lab has the lowest pass rate?'\n"
        "• 'Who are the top learners in lab 03?'\n\n"
        "Use the buttons below or just type your question!",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    router = IntentRouter(BACKEND_URL, BACKEND_API_KEY)
    await update.message.reply_text(router.route("help"), parse_mode='Markdown')

async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check backend health"""
    router = IntentRouter(BACKEND_URL, BACKEND_API_KEY)
    try:
        data = router._make_request("/items/")
        if data:
            await update.message.reply_text(f"✅ Backend is healthy. Found {len(data)} items.")
        else:
            await update.message.reply_text("❌ Backend is not responding.")
    except Exception as e:
        await update.message.reply_text(f"❌ Backend error: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    user_message = update.message.text
    logger.info(f"Received: {user_message}")
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    # Route the message
    try:
        router = IntentRouter(BACKEND_URL, BACKEND_API_KEY)
        response = router.route(user_message)
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(
            f"Sorry, I encountered an error: {e}\n\nPlease try again."
        )

def main():
    """Main entry point"""
    # Test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_message = sys.argv[2] if len(sys.argv) > 2 else "help"
        print(f"Testing: {test_message}")
        print("=" * 50)
        router = IntentRouter(BACKEND_URL, BACKEND_API_KEY)
        response = router.route(test_message)
        print(response)
        return
    
    # Normal bot mode
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        print("Error: TELEGRAM_BOT_TOKEN not set")
        print("Please set your Telegram bot token in .env.bot.secret")
        return
    
    if not BACKEND_API_KEY:
        logger.error("BACKEND_API_KEY not set!")
        print("Error: BACKEND_API_KEY not set")
        return
    
    # Create application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started! Press Ctrl+C to stop.")
    print("Bot is running... Press Ctrl+C to stop")
    app.run_polling()

if __name__ == "__main__":
    main()
