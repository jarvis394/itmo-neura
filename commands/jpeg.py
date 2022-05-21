from random import randint
from lib.command import Command
import telebot.types as types
from config.bot import MESSAGES, bot
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
from utils import generator
from lib.messages import MessagesStorage
import math
import textwrap
from config.replies import Reply


FILL_COLOR = "white"
BORDER_COLOR = "black"
BORDER_WIDTH = 3
IMAGE_FORMAT = "JPEG"
IMAGE_QUALITY = 2


def add_text(
    image: Image.Image,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    font_color=(0, 0, 0),
    border=0,
    border_color=(0, 0, 0),
    points=15,
):
    """
    Draws multiline text on a given canvas

    :image PIL.Image.Image: PIL Image
    :text str: Text to draw
    :y int: Text vertical position
    :font PIL.ImageFont.FreeTypeFont: PIL Font
    :font_color: Font color, can be string or RGB tuple
    :border int: Border width
    :border_color: Border color, can be string or RGB tuple
    :points int: Amount of curve points in border edges
    """
    draw = ImageDraw.Draw(image)
    lines = textwrap.wrap(text, width=image.width // font.getsize("a")[0] - 2)
    line_y = 0
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i]
        line_width, line_height = font.getsize(line)
        if border:
            for step in range(0, math.floor(border * points), 1):
                angle = step * 2 * math.pi / math.floor(border * points)
                border_x = (image.width - line_width) / 2 - border * math.cos(angle)
                border_y = y - border * math.sin(angle) + line_y
                draw.text(
                    (
                        border_x,
                        border_y,
                    ),
                    line,
                    border_color,
                    font=font,
                )
        draw.text(
            ((image.width - line_width) / 2, y + line_y), line, font_color, font=font
        )
        line_y -= line_height
    return image


class JpegCommand(Command):
    name = "jpeg"
    description = "Sends low-quality jpeg funny"
    aliases = ["жпег"]

    def __init__(self, *args) -> None:
        super().__init__(*args)

    async def exec(self, message: types.Message):
        await bot.send_chat_action(message.chat.id, "upload_photo")

        storage = MessagesStorage(message.chat.id)
        messages = await storage.get()
        messages.extend(
            MESSAGES.get(message.chat.id) or []
        )  # Extend storage samples with samples in memory
        sentence = generator.generate(
            samples=messages, attempts=50, max_length=randint(5, 10)
        )

        if not sentence:
            return await bot.send_message(
                message.chat.id, Reply.ON_MESSAGES_DB_TOO_SMALL
            )

        # Make text "loud"
        sentence = sentence.upper()

        # Get file information from Telegram storage API
        file_object = await bot.get_file(message.photo[-1].file_id)
        # Get binary data of the image
        file = await bot.download_file(file_object.file_path)

        buffer = BytesIO()
        img = Image.open(BytesIO(file))
        font = ImageFont.truetype("fonts/ImpactRegular.ttf", 56)
        font_size = min(img.size[0] / font.getsize_multiline(sentence)[0] * 56 * 2, 96)
        font = ImageFont.truetype("fonts/ImpactRegular.ttf", int(font_size))
        y = img.height - font.getsize(sentence)[1] - 32

        # Add randomly generated text
        add_text(img, sentence, y, font, FILL_COLOR, BORDER_WIDTH, BORDER_COLOR)

        img.save(buffer, IMAGE_FORMAT, quality=IMAGE_QUALITY)

        await bot.send_photo(message.chat.id, buffer.getvalue())
