import telebot
import requests
import os
from telebot import types
from pytube import YouTube


bot = telebot.TeleBot('6654424482:AAGbyyCQjALoVz3l-d81W8SXkE4sdwhqpI8')
languge = None

@bot.message_handler(commands=['start'])
def main(message):
    # Переводы для кнопок
    button_text_en = "🇬🇧 English"
    button_text_ru = "🇷🇺 Русский"

    # Создаем клавиатуру для выбора языка
    markup = types.InlineKeyboardMarkup(row_width=2)
    item_en = types.InlineKeyboardButton(button_text_en, callback_data='lang_en')
    item_ru = types.InlineKeyboardButton(button_text_ru, callback_data='lang_ru')
    markup.add(item_en, item_ru)

    # Приветственное сообщение с клавиатурой выбора языка
    bot.send_message(message.chat.id,
                     f'Hi, {message.from_user.first_name}! Choose a language.\n\nЗдравствуйте, {message.from_user.first_name}! Выберите язык:',
                     reply_markup=markup)


# Обработчик нажатий на инлайн-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global languge
    if call.data == 'lang_en':
        languge = 'English'
        bot.answer_callback_query(call.id, text="You have selected English.")
        # Здесь вы можете обработать выбор английского языка
        bot.send_message(call.message.chat.id, 'Send me a link.')
    elif call.data == 'lang_ru':
        languge = 'Russian'
        bot.answer_callback_query(call.id, text="Вы выбрали русский язык.")
        # Здесь вы можете обработать выбор русского языка
        bot.send_message(call.message.chat.id, 'Введите ссылку на YouTube ролик.')

#Обработчик ссылок
@bot.message_handler(func=lambda message: True)
#обработчик длинных ссыло
def handle_one(message):
    try:
        video_url = message.text   # Создаем объект YouTube с помощью pytube
        youtube_video = YouTube(video_url)

        audio_streams = youtube_video.streams.filter(only_audio=True)
        max_bitrate_audio = audio_streams.get_audio_only()
        #audio_file_path = f"{youtube_video.title}.mp3"
        downloaded_file_path = max_bitrate_audio.download()

        with open(downloaded_file_path, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file)

        # Удаляем файл после отправки
        os.remove(downloaded_file_path)

        bot.send_message(message.chat.id, f"{youtube_video.title}")
    except:
        #Обработчик коротких ссылок
        try:
            def expand_short_url(short_url):
                response = requests.head(short_url, allow_redirects=True)
                expanded_url = response.url
                return expanded_url

            video_url = message.text
            expanded_url = expand_short_url(video_url)
            youtube_video = YouTube(expanded_url)

            audio_streams = youtube_video.streams.filter(only_audio=True)
            max_bitrate_audio = audio_streams.get_audio_only()
            # audio_file_path = f"{youtube_video.title}.mp3"
            downloaded_file_path = max_bitrate_audio.download()

            with open(downloaded_file_path, 'rb') as audio_file:
                bot.send_audio(message.chat.id, audio_file)

            # Удаляем файл после отправки
            os.remove(downloaded_file_path)

            bot.send_message(message.chat.id, f"{youtube_video.title}")
        #Обрабатываем некоректные ссылки
        except:
            if video_url.startswith('https://www.youtube.com'):
                if languge == "English":
                    bot.send_message(message.chat.id, "Unfortunately, I couldn't find the video on YouYube.\n\nCheck the correctness of the link.")
                elif languge == "Russian":
                    bot.send_message(message.chat.id, "К сожалению, я не смог найти данное видео на YouTube.\n\nПроверьте корректность ссылки.")
            elif video_url.startswith('https://'):
                if languge == "English":
                    bot.send_message(message.chat.id, f"Unfortunately, I couldn't process your link:\n{video_url}\n\nCheck if this is a link to YouTube")
                elif languge == "Russian":
                    bot.send_message(message.chat.id, f"К сожалению, я не смог обработать вашу ссылку:\n{video_url}\n\nПроверьте, является ли это ссылкой на YouTube")
            else:
                if languge == "English":
                    bot.send_message(message.chat.id, f"I couldn't find the link in your message\n\nGive me a link")
                elif languge == "Russian":
                    bot.send_message(message.chat.id, "Я не смог найти ссылку в вашем сообщении\n\nДайте мне ссылку")

# Запуск бота
bot.polling(none_stop=True)