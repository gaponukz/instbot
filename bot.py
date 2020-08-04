''' Bot for sending top posts from instagram '''

from aiogram import Bot, Dispatcher, executor, types # all for bot

from config import * # texts (help...)
from db import SQLite as Database # sqlite database
from instaparser import (
	InstaUser, Post, get_posts,
	filter_by_date, sort
)  # main parser

# 1201136195:AAGr1ioNsrOHqTfJAg_JeOV6FzuxU-RatDI - @sometestbotforparsingbot
API_TOKEN = '925387553:AAHxDgs0QseQ1ugzQWOi6Z6NuP-ovxy07EY'
bot = Bot(token = API_TOKEN)
dp = Dispatcher(bot)
db = Database('users.db')

@dp.callback_query_handler(lambda callback: True)
async def process_callback_button(callback_query: types.CallbackQuery):
	data = callback_query.data.split()
	await bot.send_message(callback_query.from_user.id, "Processing...")

	user = InstaUser(data[0])
	if data[1] == 'likes':
		if len(data) > 3:
			posts = filter_by_date(sort(get_posts(user.account),\
				by = 'likes'), _from = data[3], _to = data[4])
		else:
			posts = sort(get_posts(user.account), by = 'likes')

	elif data[1] == 'comments':
		if len(data) > 3:
			posts = filter_by_date(sort(get_posts(user.account),\
				by = 'comments'), _from = data[3], _to = data[4])
		else:
			posts = sort(get_posts(user.account), by = 'comments')

	elif data[1] == 'posts':
		posts = filter_by_date(get_posts(user.account),\
			_from = data[3], _to = data[4])

	if posts[int(data[2]):int(data[2])+10]:
		for post in posts[int(data[2]):int(data[2])+10]:
			try:
				media = list(map(lambda x: types.InputMediaPhoto(x), post['images']))

				media[-1] = types.InputMediaPhoto(post['images'][-1], caption = \
					message_text.format(post['description'],
					post['likes_count'], post['comment_count'], post['post_url']))

				await bot.send_media_group(callback_query.from_user.id, media)

			except:
				pass

		if len(data) > 3:
			inline_btn = types.InlineKeyboardButton('Show more', callback_data = \
				f"{user.account} {data[1]} {int(data[2])+10} {data[3]} {data[4]}")
		else:
			inline_btn = types.InlineKeyboardButton('Show more', callback_data = \
			f"{user.account} {data[1]} {int(data[2])+10}")

		inline = types.InlineKeyboardMarkup(row_width = 2).add(inline_btn)

		await callback_query.message.answer("Press the button to show more", reply_markup = inline)

	else:
		await bot.send_message(callback_query.from_user.id, "No more posts")


@dp.message_handler(commands = ['likes'])
async def likes(message: types.Message):
	arguments = message.get_args().split()
	if arguments:
		try:
			await bot.send_message(message.from_user.id, "Processing...")

			user = InstaUser(arguments[0])

			if user.is_public:
				if len(arguments) == 1:
					posts = sort(get_posts(user.account), by = 'likes')
				else:
					posts = filter_by_date(sort(get_posts(user.account),\
					by = 'likes'), _from = arguments[1], _to = arguments[3])

				for post in posts[:10]:
					try:
						media = list(map(lambda x: types.InputMediaPhoto(x), post['images']))

						media[-1] = types.InputMediaPhoto(post['images'][-1], caption = \
							message_text.format(post['description'],
							post['likes_count'], post['comment_count'], post['post_url']))

						await bot.send_media_group(message.from_user.id, media)
					except:
						pass

				if len(arguments) == 1:
					inline_btn = types.InlineKeyboardButton('Show more', \
					callback_data = f"{user.account} likes 10")
				else:
					inline_btn = types.InlineKeyboardButton('Show more', \
					 callback_data = f"{user.account} likes 10 {arguments[1]} {arguments[3]}")

				inline = types.InlineKeyboardMarkup(row_width = 2).add(inline_btn)
				await message.answer("Press the button to show more", reply_markup = inline)

			else:
				lang = 1 if message.from_user.language_code == 'ru' else 0

				await message.answer(text['private'][lang])
		except:
			await bot.send_message(message.from_user.id, "Account does not exist!")

@dp.message_handler(commands = ['comments'])
async def comments(message: types.Message):
	arguments = message.get_args().split()
	if arguments:
		try:
			await bot.send_message(message.from_user.id, "Processing...")

			user = InstaUser(arguments[0])

			if user.is_public:
				if len(arguments) == 1:
					posts = sort(get_posts(user.account), by = 'comments')
				else:
					posts = filter_by_date(sort(get_posts(user.account),\
					by = 'comments'), _from = arguments[1], _to = arguments[3])

				for post in posts[:10]:
					try:
						media = list(map(lambda x: types.InputMediaPhoto(x), post['images']))

						media[-1] = types.InputMediaPhoto(post['images'][-1], caption = \
							message_text.format(post['description'],
							post['likes_count'], post['comment_count'], post['post_url']))

						await bot.send_media_group(message.from_user.id, media)

					except:
						await bot.send_message(message.from_user.id, "Account does not exist!")

				if len(arguments) == 1:
					inline_btn = types.InlineKeyboardButton('Show more', \
					callback_data = f"{user.account} likes 10")
				else:
					inline_btn = types.InlineKeyboardButton('Show more', callback_data = \
					f"{user.account} likes 10 {arguments[1]} {arguments[3]}")

				inline = types.InlineKeyboardMarkup(row_width = 2).add(inline_btn)
				await message.answer("Press the button to show more", reply_markup = inline)

			else:
				lang = 1 if message.from_user.language_code == 'ru' else 0

				await message.answer(text['private'][lang])

		except:
			await bot.send_message(message.from_user.id, "Account does not exist!")

@dp.message_handler(commands = ['posts'])
async def posts(message: types.Message):
	arguments = message.get_args().split()
	if arguments:
		try:
			await bot.send_message(message.from_user.id, "Processing...")

			user = InstaUser(arguments[0])

			if user.is_public:
				posts = filter_by_date(get_posts(user.account),\
					_from = arguments[1], _to = arguments[3])

				for post in posts[:10]:
					try:
						media = list(map(lambda x: types.InputMediaPhoto(x), post['images']))

						media[-1] = types.InputMediaPhoto(post['images'][-1], caption = \
							message_text.format(post['description'],
							post['likes_count'], post['comment_count'], post['post_url']))

						await bot.send_media_group(message.from_user.id, media)

					except:
						pass

				if len(arguments) == 1:
					inline_btn = types.InlineKeyboardButton('Show more', \
					callback_data = f"{user.account} likes 10")
				else:
					inline_btn = types.InlineKeyboardButton('Show more', callback_data = \
					f"{user.account} likes 10 {arguments[1]} {arguments[3]}")

				inline = types.InlineKeyboardMarkup(row_width = 2).add(inline_btn)
				await message.answer("Press the button to show more", reply_markup = inline)

			else:
				lang = 1 if message.from_user.language_code == 'ru' else 0

				await message.answer(text['private'][lang])
		except:
			await bot.send_message(message.from_user.id, "Account does not exist!")

@dp.message_handler(commands = ['account'])
async def account(message: types.Message):
	arguments = message.get_args().split()
	if arguments:
		try:
			account = InstaUser(arguments[0])

			media = types.InputMediaPhoto(account.profile_pic_url, caption = \
				account_message_text.format(account.biography, '' \
				if not account.external_url else account.external_url, \
				account.followed_count, account.follow_count, account.posts_count, \
				f'https://instagram.com/{account.account}')
			)

			await bot.send_media_group(message.from_user.id, [media])
		except:
			pass

@dp.message_handler(commands = ['language'])
async def language(message: types.Message):
	arguments = message.get_args().split()
	if arguments: message.from_user.language_code = arguments[0]

@dp.message_handler(commands = ['help'])
async def help(message: types.Message):
	lang = 1 if message.from_user.language_code == 'ru' else 0
	await message.answer(text['help_text'][lang])

@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
	if not db.user_exists(message.from_user.id):
		db.add_user(message.from_user.id, message.from_user.username)
	
	await message.answer('Hello! I am Instagram Sorting Bot. Write /help to see the list of commands.')

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates = True)