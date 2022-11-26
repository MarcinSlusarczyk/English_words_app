# pip install python-telegram-bot
from telegram.ext import *
import keys
import sys
from googletrans import Translator
import pandas as pd
import datetime
import pytz

print(f"nauka słowek uruchomiona {datetime.time(hour=11, minute=28)}" )

def start_command(update, context):
    update.message.reply_text('Siemka! jakie słowka chcesz powtórzyć/dodać?')

def help_command(update, context):
    update.message.reply_text('na tą chwilę możesz: '
                              '\n\n  - sprawdzać tłumaczenia słów'
                              '\n  - zapisywać frazy o słowka i uczyć się ich!'
                              )

def add_translate(update, context):

    text = update.message.text[5:]
    if text != '':
        translator = Translator()
        lang = translator.detect(text).lang
        if lang == "pl":
            translated = translator.translate(text, dest='en').text
            update.message.reply_text(f'PL: {text} \nENG: {translated}')
            data = {'Polski': [text], 'Angielski': [translated]}
            df = pd.DataFrame(data, columns = ["Polski", "Angielski"])
            df.to_csv('english_dict.csv', mode='a+', sep=";", index=False, header=False, encoding="UTF-8")

        else:
            translated = translator.translate(text, dest='pl').text
            update.message.reply_text(f'ENG: {text} \nPL: {translated}')
            data = {'Polski': [translated], 'Angielski': [text]}
            df = pd.DataFrame(data, columns = ["Polski", "Angielski"])
            df.to_csv('english_dict.csv', mode='a+', sep=";", index=False, header=False, encoding="UTF-8")

def delete_word(update, context):
    text = update.message.text[5:]
    if text != "":
        update.message.reply_text(f'usuwam: {text}')
        df = pd.read_csv("english_dict.csv", encoding="UTF-8", sep=";", header=None)
        df = df[(df[1] != text)]
        df.to_csv('english_dict.csv', mode='w', sep=";", index=False, header=False, encoding="UTF-8")
        show_words(update, context)

def show_words(update, context):
        df = pd.read_csv("english_dict.csv", encoding="UTF-8", sep=";",  header=None)
        output = ""
        for index, row in df.iterrows():
            output = output + f"{row[0]} - {row[1]}\n"
        update.message.reply_text(f"MÓJ SŁOWNIK:\n\n" + output)

def send_random_words(context):
    df = pd.read_csv("english_dict.csv", encoding="UTF-8", header=None)
    random_words = df.sample()
    output = f"PL: {random_words[0].values[0]}\nENG: {random_words[1].values[0]}"
    context.bot.send_message(chat_id='5644184941', text=f"FISZKA NA DZIŚ:\n\n" + output)

def start_auto_lessons(update, context):
    chat_id = update.message.chat_id
    # context.job_queue.run_repeating(send_random_words, 5, context=chat_id, name=str(chat_id))
    # context.job_queue.run_once(send_random_words, 3600, context=chat_id)
    context.job_queue.run_daily(send_random_words, time=datetime.time(hour=8, minute=00), days=(0, 1, 2, 3, 4, 5, 6), context=chat_id, name="alert_rano") # back - 1 hour
    context.job_queue.run_daily(send_random_words, time=datetime.time(hour=19, minute=00), days=(0, 1, 2, 3, 4, 5, 6), context=chat_id, name="alert_wieczor") # back - 1 hour

def stop_auto_lessons(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text='Wyłączam automatyczne fiszki!')
    job = context.job_queue.get_jobs_by_name("alert_rano")
    job[0].schedule_removal()

    job = context.job_queue.get_jobs_by_name("alert_wieczor")
    job[0].schedule_removal()



def handle_message(update, context):

    text = str(update.message.text).lower()

    if text in ('hello', 'cześć', 'hej'):
        update.message.reply_text("No cześć!")
        return text

    elif text in ('jak leci?', 'co tam?'):
        update.message.reply_text("Wszystko ok! ")
        return text

    elif text in ('/exit'):
        update.message.reply_text("Kończymy nauke angielskiego!")
        sys.exit()

    else:
        update.message.reply_text("Nie rozumiem co napisałeś :(")

def error(update, context):
    print(f'Update {update} powód błędu {context.error}')

# Run the program
if __name__ == '__main__':

    updater = Updater(keys.token, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('pomoc', help_command))
    dp.add_handler(CommandHandler('add', add_translate))
    dp.add_handler(CommandHandler('del', delete_word))
    dp.add_handler(CommandHandler('show', show_words))
    dp.add_handler(CommandHandler("auto", start_auto_lessons))
    dp.add_handler(CommandHandler("stop", stop_auto_lessons))
    # Messages
    dp.add_handler(MessageHandler(Filters.text, handle_message))
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()