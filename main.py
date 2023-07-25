from typing import Final
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import requests
from firebase_connection import update_module, find_friends, get_modules, delete_module

TOKEN: Final = ''  # Please ask owner for TOKEN
BOT_USERNAME: Final = '@lighthouseModsBot'

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('To begin, select /add_module.')

async def add_modules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['add_module_mode'] = True
    context.user_data['delete_module_mode'] = False
    await update.message.reply_text("Please enter a module code. Eg: CS1101S. If you do not wish to add a module, please enter 'done'")

async def find_module_friends_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    Calls find_friends from firebase_connection to return a list, with each element consisting of a 2-element tuple, with index 0 being module code and index 1 being the list of people taking the module. 
    Eg: [('CS1234', ['nicrandomlee', 'charltonteo']), ('CS1235', ['nicrandomlee'])]
    '''

    telehandle: str = update.message.from_user.username #tele handle

    involved_modules = find_friends(telehandle)
    message = "People taking the same modules as you this semester: \n"
    for mod, mod_student_list in involved_modules:
        message = message + '\n' + mod + '\n'
        message = message + '\n'.join(("@" + str(student)) for student in mod_student_list)
        message += '\n'

    await update.message.reply_text(message)

async def delete_module_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['add_module_mode'] = False
    telehandle: str = update.message.from_user.username #tele handle

    all_modules_list = get_modules(telehandle)

    if len(all_modules_list) == 0:
        await update.message.reply_text("You do not have any modules. Run /add_module to add modules.")
        
    keyboard = [all_modules_list]
    await update.message.reply_text('Which module do you want to delete?', 
                                    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True))
    context.user_data['delete_module_mode'] = True
    

def delete_module_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['delete_module_mode'] = False

    telehandle: str = update.message.from_user.username #tele handle
    module_code: str = update.message.text  # Incoming message
    
    delete_module(telehandle, module_code)

    return "Module deleted. Please run /delete_module again if you wish to delete more modules."

#####################
# Message Handling  #
#####################
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Inform if it is group or private chat
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle

    # UserID, group/private chat/ incoming message
    print(f'User {telehandle} ({update.message.chat.id}) in {message_type}: {text}')
    
    context.user_data.setdefault('add_module_mode', False)
    context.user_data.setdefault('delete_module_mode', False)

    if context.user_data['add_module_mode']:
        response = handle_add_module_response(update, context)
    
    elif context.user_data['delete_module_mode']:
        response = delete_module_handler(update, context)
    else: 
        response = handle_response(text, telehandle)
        pass

    print('Bot:', response)  # For debugging
    await update.message.reply_text(response)

def handle_add_module_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    print("handle_add_module_response")
    message_type: str = update.message.chat.type #message type
    text: str = update.message.text  # Incoming message
    telehandle: str = update.message.from_user.username #tele handle

    #Change all module codes
    text = text.strip().upper()

    if text == "DONE":
        context.user_data['add_module_mode'] = False
        return "To look for residents taking the same modules, please run /find_module_friends!"

    if not 6 <= len(text) <= 8:
        return "Invalid module code. Please enter another module."
    
    # Updating Firebase
    error_message = update_module(telehandle, text)

    if error_message:
        return error_message

    return f"Module {text} added. If you wish to, you may add another module. Eg: CS1101S. If you do not wish to add a module, please enter 'done'"


def handle_response(text: str, telehandle: str) -> str:
    return "I do not understand what you mean! Run /start to begin."


if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('add_module', add_modules_command))
    app.add_handler(CommandHandler('find_module_friends', find_module_friends_command))
    app.add_handler(CommandHandler('delete_module', delete_module_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors

    # Polls the bot
    print('Polling...')
    app.run_polling(poll_interval=3)  # Checks every x seconds for messages