import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json

# Logging konfiguratsiyasi
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Fayllar
TESTS_FILE = 'tests.json'
RESULTS_FILE = 'results.json'

# Testlarni yuklash/yangi yaratish
def load_tests():
    if os.path.exists(TESTS_FILE):
        with open(TESTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_tests(tests):
    with open(TESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tests, f, ensure_ascii=False, indent=2)

# Natijalarni yuklash/yangi yaratish
def load_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_results(results):
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Salom! Testnike botga xush kelibsiz. /help buyrug\'ini ishlatib ko\'ring.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
Buyruqlar:
/start - Botni ishga tushirish
/help - Yordam
/add_test - Yangi test qo\'shish
Natija yuborish: Test ID va javoblaringizni yuboring, masalan: "test1 A B C"
    """
    await update.message.reply_text(help_text)

async def add_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text('Foydalanish: /add_test <test_id> <savol> <to\'g\'ri_javob>')
        return
    
    test_id = context.args[0]
    question = ' '.join(context.args[1:-1])
    correct_answer = context.args[-1].upper()
    
    tests = load_tests()
    tests[test_id] = {
        'question': question,
        'correct_answer': correct_answer
    }
    save_tests(tests)
    
    await update.message.reply_text(f'Test {test_id} muvaffaqiyatli qo\'shildi: {question}\nTo\'g\'ri javob: {correct_answer}')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Test natijasini tekshirish
    if ' ' in text:
        parts = text.split(' ', 1)
        test_id = parts[0].lower()
        user_answer = parts[1].upper().strip()
        
        tests = load_tests()
        if test_id in tests:
            correct = tests[test_id]['correct_answer']
            is_correct = user_answer == correct
            
            result = {
                'user_id': update.effective_user.id,
                'username': update.effective_user.username or 'Noma\'lum',
                'test_id': test_id,
                'user_answer': user_answer,
                'correct_answer': correct,
                'is_correct': is_correct,
                'timestamp': update.message.date.isoformat()
            }
            
            results = load_results()
            if test_id not in results:
                results[test_id] = []
            results[test_id].append(result)
            save_results(results)
            
            if is_correct:
                await update.message.reply_text('To\'g\'ri! ✅')
            else:
                await update.message.reply_text(f'Noto\'g\'ri. To\'g\'ri javob: {correct} ❌')
        else:
            await update.message.reply_text('Bunday test topilmadi. Mavjud testlar: ' + ', '.join(tests.keys()))
    else:
        await update.message.reply_text('Test ID va javob yuboring, masalan: test1 A')

def main():
    # Bot tokenini environment variable dan olish
    TOKEN = os.getenv('BOT_TOKEN')
    if not TOKEN:
        logger.error("BOT_TOKEN environment variable topilmadi!")
        return
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('add_test', add_test))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Railway uchun polling
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
