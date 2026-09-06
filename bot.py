import telebot, asyncio, aiohttp, json, random, re, os, string, time, uuid
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web
import cv2
import ddddocr
import numpy as np
from datetime import datetime, timedelta, timezone

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8943265654:AAGyQanRALHAWZ7ZOSTzQKdOx_FfOFPa2Xo"

ADMINS = [
    "8937162965",
]

ADMIN_USERNAME = "@Hann13"

def is_admin(user_id):
    return str(user_id) in ADMINS

PROXY_LIST = [
    "w9nx03l4kl8vdf0:iwx3ijrwgcyil91@rp.scrapegw.com:6060",
]

_proxy_index = 0
def get_next_proxy():
    global _proxy_index
    if not PROXY_LIST:
        return None
    proxy = PROXY_LIST[_proxy_index % len(PROXY_LIST)]
    _proxy_index += 1
    return f"http://{proxy}"

SUCCESS_CODE = asyncio.Queue()
bot = AsyncTeleBot(BOT_TOKEN)
user_data = {}
scan_tasks = {}
success_messages = {}
success_texts = {}
limited_messages = {}
limited_texts = {}
captcha_state = {}
session = None
_connector = None
CONCURRENCY = 5000  # Bot Speed မြင့်ရန် Concurrency ကို တိုးမြှင့်ထားသည်
_voucher_sem = None
_start_time = time.monotonic()

MAX_CONCURRENT_SCANS = 100
active_scans_count = 0
active_scans_lock = asyncio.Lock()

async def handle(request):
    return web.Response(text="Bot is awake and running 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('BOT_PORT', 8099))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔗 STAR LINK Portal URL ထည့်ရန်", callback_data="menu_free_trial"),
        InlineKeyboardButton("📋 Success Codes ကြည့်မည်", callback_data="menu_result"),
        InlineKeyboardButton("🔄 Recheck ပြန်လုပ်စစ်မည်", callback_data="menu_recheck"),
        InlineKeyboardButton("🛑 Scan ရပ်မည်", callback_data="menu_stop"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

def get_voucher_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🔢 VOUCHER 6 လုံး", callback_data="scan_6"),
        InlineKeyboardButton("🔢 VOUCHER 7 လုံး", callback_data="scan_7"),
        InlineKeyboardButton("🔢 VOUCHER 8 လုံး", callback_data="scan_8"),
        InlineKeyboardButton("🔢 VOUCHER 9 လုံး", callback_data="scan_9"),
        InlineKeyboardButton("🔤 VOUCHER ascii-lower", callback_data="scan_ascii-lower"),
        InlineKeyboardButton("🔤 VOUCHER ascii-lower 9လုံး", callback_data="scan_ascii-lower9"),
        InlineKeyboardButton("🎲 VOUCHER all", callback_data="scan_all"),
        InlineKeyboardButton("🔤+🔢 MIXED 6လုံး", callback_data="scan_mixed"),
        InlineKeyboardButton("🔤+🔢 MIXED 8လုံး", callback_data="scan_mixed8"),
        InlineKeyboardButton("🔤+🔢 MIXED 9လုံး", callback_data="scan_mixed9"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

def get_start_scam_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🚀 START SCAN", callback_data="menu_start_scam"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

def get_back_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("🔙 Back", callback_data="menu_back"))
    return keyboard

def get_scam_button_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🛑 STOP SCAN", callback_data="menu_stop"),
        InlineKeyboardButton("🔙 Back", callback_data="menu_back")
    )
    return keyboard

@bot.message_handler(commands=['start'])
async def start(message):
    user_id = str(message.chat.id)
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if message.chat.id not in user_data:
        user_data[message.chat.id] = {}
    
    welcome_text = f"""✨ STAR LINK CODE HACK ✨

👤 NAME: {user_name}
🆔 USER ID: {user_id}

🎉 မင်္ဂလာပါခင်ဗျာ! 
🚀 အမြန်နှုန်းအမြင့်ဆုံးဖြင့် အသုံးပြုနိုင်ပါသည်။
👨‍💻 Admin: {ADMIN_USERNAME}

အောက်ပါ Menu မှ သင်လိုချင်တာကိုရွေးချယ်ပါ။"""
    
    await bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
async def callback_handler(call):
    chat_id = call.message.chat.id
    user_id = str(chat_id)
    user_name = call.from_user.first_name or call.from_user.username or "User"
    
    if call.data == "menu_back":
        text = f"""✨ STAR LINK CODE HACK ✨

👤 NAME: {user_name}
🆔 USER ID: {user_id}

🚀 High Speed Mode Active"""
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_main_keyboard()
        )
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_free_trial":
        text = f"""🔗 Portal URL ထည့်သွင်းရန်:

/portal [your_portal_url]

ဥပမာ:
/portal https://portal-as.ruijienetworks.com/download/static/maccauth/src/index.html?lang=en_US&mac=02:00:00:00:00:00"""
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_back_keyboard()
        )
        await bot.answer_callback_query(call.id)
        return
    
    if call.data == "menu_result":
        if chat_id in user_data and 'found_codes' in user_data[chat_id] and user_data[chat_id]['found_codes']:
            codes = "\n".join(user_data[chat_id]['found_codes'])
            text = f"✅ Found Codes:\n{codes}"
        else:
            text = "📋 သင့်တွင် ယခင်ကရရှိထားသော success code မရှိသေးပါ။"
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=get_back_keyboard()
        )
        await bot.answer_callback_query(call.id)
        return

    if call.data == "menu_stop":
        if chat_id in scan_tasks:
            scan_tasks[chat_id]["stop"] = True
        await bot.answer_callback_query(call.id, "🛑 Scan ကိုရပ်တန့်လိုက်ပါပြီ။", show_alert=True)
        return
    
    if call.data.startswith("scan_"):
        mode = call.data.replace("scan_", "")
        if chat_id not in user_data:
            user_data[chat_id] = {}
        user_data[chat_id]['selected_mode'] = mode
        
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"🚀 ရွေးချယ်ထားသော Mode: {mode}\n\nစတင်ရန် START SCAN ကိုနှိပ်ပါက စတင်နိုင်ပါသည်။",
            reply_markup=get_start_scam_keyboard()
        )
        await bot.answer_callback_query(call.id)
        return

async def main():
    global session
    conn = aiohttp.TCPConnector(limit=CONCURRENCY, ttl_dns_cache=300, ssl=False)
    session = aiohttp.ClientSession(connector=conn)
    asyncio.create_task(web_server())
    print("High-speed Bot is running...")
    await bot.infinity_polling()

if __name__ == '__main__':
    asyncio.run(main())
