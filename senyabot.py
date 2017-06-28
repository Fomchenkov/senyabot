#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

import flask
import telebot
from telebot import types


data = [{
	"text": "Привет! Я бот Сеня! Я помогаю людям оформлять страховые полисы. Какой из видов страхования Вас интересует?",
	"keyboard": "ОСАГО;ЗЕЛЕНАЯ КАРТА;КАСКО;Имущество;Жизнь и Здоровье"
}, {
	"text": "Как Вам удобней забрать готовый полис?",
	"keyboard": "Приехать в офис продаж;Бесплатная доставка"
}, {
	"text": "Напишите Ваше имя и номер телефона и наш менеджер сделает Вам лучшее предложение или приезжайте к нам в офис по адресу: г.Смоленск Краснинское шоссе д.14 (Автомойка МИГ 2 этаж), офис 15Б.\n\nТел: 8-930-305-80-01\n\n54-80-01"
}]


BOT_TOKEN = '361985287:AAERpy1Zlw-ID0UAysU6lO_-l63mm0RvKNc' # sys.argv[1]
USERS_STEPS = {}
USERS_DATA = {}
MANAGER_ID = 217166737


WEBHOOK_HOST = '89.223.25.123'
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{!s}:{!s}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{!s}/".format(BOT_TOKEN)

bot = telebot.TeleBot(BOT_TOKEN)
app = flask.Flask(__name__)


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
	if flask.request.headers.get('content-type') == 'application/json':
		json_string = flask.request.get_data().decode('utf-8')
		update = telebot.types.Update.de_json(json_string)
		bot.process_new_updates([update])
		return ''
	else:
		flask.abort(403)


def build_keyboard(string):
	"""
	Build Telegram keyboard from string
	:param: string (format "Key1;Key2;Key3")
	:return: markup object
	"""
	str_arr = string.split(";")
	markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
	for command in str_arr:
		markup.add(types.KeyboardButton(text=command))
	return markup


@bot.message_handler(commands=['start'])
def start_command(message):
	uid = message.from_user.id

	USERS_STEPS[str(uid)] = 0
	USERS_DATA[str(uid)] = 'Имя пользователя: ' + str(message.from_user.first_name) + '.\n\n'
	text = data[USERS_STEPS[str(uid)]]['text']
	keyboard = types.ReplyKeyboardRemove()

	if 'keyboard' in data[USERS_STEPS[str(uid)]]:
		keyboard = build_keyboard(data[USERS_STEPS[str(uid)]]['keyboard'])

	return bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='markdown')


@bot.message_handler(content_types=['text'])
def text_handler(message):
	uid = message.from_user.id

	if not str(uid) in USERS_STEPS:
		text = 'Отправь мне команду /start, что бы начать!'
		return bot.send_message(message.chat.id, text, parse_mode='markdown')

	if USERS_STEPS[str(uid)] == 0:
		if message.text == "ОСАГО" or message.text == "ЗЕЛЕНАЯ КАРТА":
			USERS_DATA[str(uid)] += message.text + '\n\n'
			USERS_STEPS[str(uid)] += 1
		elif message.text == "КАСКО" or message.text == "Имущество" or message.text == "Жизнь и Здоровье":
			USERS_DATA[str(uid)] += message.text + '\n\n'
			USERS_STEPS[str(uid)] += 2
		else:
			text = 'Пожалуйста, выберите пункт из списка.'
			return bot.send_message(uid, text, parse_mode='markdown')

		text = data[USERS_STEPS[str(uid)]]['text']
		keyboard = types.ReplyKeyboardRemove()
		if 'keyboard' in data[USERS_STEPS[str(uid)]]:
			keyboard = build_keyboard(data[USERS_STEPS[str(uid)]]['keyboard'])
		return bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='markdown')

	USERS_DATA[str(uid)] += message.text + '\n\n'
	USERS_STEPS[str(uid)] += 1

	print(USERS_DATA, '\n', USERS_STEPS)

	# Check to end
	if USERS_STEPS[str(uid)] >= len(data):
		userdata = USERS_DATA[str(uid)]
		del USERS_DATA[str(uid)]
		del USERS_STEPS[str(uid)]
		bot.send_message(MANAGER_ID, userdata, parse_mode='markdown')
		text = 'Спасибо за использование нашего бота!'
		print(USERS_DATA, '\n', USERS_STEPS)
		return bot.send_message(uid, text, parse_mode='markdown')

	text = data[USERS_STEPS[str(uid)]]['text']
	keyboard = types.ReplyKeyboardRemove()

	if 'keyboard' in data[USERS_STEPS[str(uid)]]:
		keyboard = build_keyboard(data[USERS_STEPS[str(uid)]]['keyboard'])

	return bot.send_message(message.chat.id, text, reply_markup=keyboard, parse_mode='markdown')


def main():
	bot.polling(none_stop=True)
	"""
	bot.remove_webhook()
	time.sleep(1)
	bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH,
					certificate=open(WEBHOOK_SSL_CERT, 'r'))
	app.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT,
			ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV))
	"""


if __name__ == '__main__':
	main()
