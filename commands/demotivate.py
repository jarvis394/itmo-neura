from lib.messages import MessagesStorage
from lib.command import Command
import telebot.types as types
from utils import generator
from config.replies import Reply
from config.bot import bot, MESSAGES
import io
from PIL import Image, ImageDraw, ImageFont

BACKGROUND_WIDTH = 1000
PADDING = 100
PADDING_Y = 80
BORDER_PADDING = 14
TITLE_TEXT_SIZE = 64
LOWER_TEXT_SIZE = 40
TEXT_SPACING = 18
SPACE = 24
TEXT_ANCHOR = 'mt'
TEXT_ALIGN = 'center'
TITLE_TEXT_FONT = ImageFont.truetype("fonts/TimesNewRoman.ttf", TITLE_TEXT_SIZE)
LOWER_TEXT_FONT = ImageFont.truetype("fonts/ImpactRegular.ttf", LOWER_TEXT_SIZE)

TITLE_TEXT_SPACING = TEXT_SPACING + TITLE_TEXT_SIZE
LOWER_TEXT_SPACING = TEXT_SPACING // 1.7 + LOWER_TEXT_SIZE

def generate_multiline_text(text: str, max_width: int, font: ImageFont.ImageFont, spacing: int):
	background_draw = ImageDraw.Draw(Image.new('RGB', (BACKGROUND_WIDTH, BACKGROUND_WIDTH)))
	words = text.split(' ')
	current_line_text = words[0]
	text_lines = []

	for word in words[1:]:
		temp_width, _ = background_draw.multiline_textsize(f'{current_line_text} {word}',
		                                                   font=font,
		                                                   spacing=spacing)
		if temp_width < max_width:
			current_line_text = f'{current_line_text} {word}'
		else:
			text_lines.append(current_line_text)
			current_line_text = word

	text_lines.append(current_line_text)

	return text_lines

class DemotivateCommand(Command):
	name = "demotivate"
	description = "Generates random demotivator iamge based on chat history"
	aliases = ["dem", "демотиватор", "дем"]

	def __init__(self, *args) -> None:
		super().__init__(*args)

	async def exec(self, message: types.Message):

		await bot.send_chat_action(message.chat.id, "upload_photo")

		storage = MessagesStorage(message.chat.id)
		messages = await storage.get()
		messages.extend(MESSAGES.get(message.chat.id) or [])  # Extend storage samples with samples in memory

		title_text = generator.generate(samples=messages, attempts=50)
		lower_text = generator.generate(samples=messages, attempts=50)

		if not title_text:
			return await bot.send_message(message.chat.id, Reply.ON_MESSAGES_DB_TOO_SMALL)

		max_text_width = BACKGROUND_WIDTH - 2 * PADDING
		multiline_title_text = generate_multiline_text(title_text, max_text_width, TITLE_TEXT_FONT, TEXT_SPACING)
		multiline_lower_text = generate_multiline_text(lower_text, max_text_width, LOWER_TEXT_FONT,
		                                               TEXT_SPACING // 1.7)

		image_file_info = await bot.get_file(message.photo[-1].file_id)
		image = await bot.download_file(image_file_info.file_path)
		image = Image.open(io.BytesIO(image))

		image_width = BACKGROUND_WIDTH - 2 * PADDING
		image_height = image.height * image_width // image.width
		image.thumbnail((image_width, image_height), Image.ANTIALIAS)

		calculated_background_height = 2 * PADDING_Y + 2 * BORDER_PADDING + image.height + len(
		    multiline_title_text) * TITLE_TEXT_SPACING - TEXT_SPACING + (
		        len(multiline_lower_text) * LOWER_TEXT_SPACING - TEXT_SPACING // 1.7 if lower_text else 0)

		background = Image.new('RGB', (BACKGROUND_WIDTH, int(calculated_background_height)))
		background_draw = ImageDraw.Draw(background)

		background.paste(image, (BACKGROUND_WIDTH // 2 - image_width // 2, PADDING_Y + BORDER_PADDING))
		background_draw.rectangle(
		    (BACKGROUND_WIDTH // 2 - image_width // 2 - BORDER_PADDING, PADDING_Y, BACKGROUND_WIDTH // 2 +
		     image_width // 2 + BORDER_PADDING, PADDING_Y + image_height + 2 * BORDER_PADDING),
		    outline=(255, 255, 255),
		    width=4)

		start_text_position = PADDING_Y + image_height + 2 * BORDER_PADDING + SPACE

		for i, title_text_line in enumerate(multiline_title_text):
			background_draw.text((BACKGROUND_WIDTH // 2, start_text_position + TITLE_TEXT_SPACING * i),
			                     title_text_line,
			                     fill=(255, 255, 255),
			                     font=TITLE_TEXT_FONT,
			                     spacing=TEXT_SPACING,
			                     anchor=TEXT_ANCHOR,
			                     align=TEXT_ALIGN)

		if lower_text:
			for i, lower_text_line in enumerate(multiline_lower_text):
				background_draw.text(
				    (BACKGROUND_WIDTH // 2,
				     start_text_position + TITLE_TEXT_SPACING * len(multiline_title_text) + LOWER_TEXT_SPACING * i),
				    lower_text_line,
				    fill=(255, 255, 255),
				    font=LOWER_TEXT_FONT,
				    spacing=TEXT_SPACING,
				    anchor=TEXT_ANCHOR,
				    align=TEXT_ALIGN)

		background_bytes = io.BytesIO()
		background.save(background_bytes, 'JPEG')

		await bot.send_photo(message.chat.id, background_bytes.getvalue())
