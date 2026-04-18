# test-bot(bot class)
# This example requires the 'members' and 'message_content' privileged intents to function.

import asyncio
import discord
import random
import math
from discord.ext import commands
from bot_logic import gen_pass
import os
import requests
from bot_logic import gen_pass, coinflip as bot_coinflip, roll_dice
from model import get_class
from detect_objects import detect
from collections import Counter

EMISSION_FACTORS = {
    'car': 120,       
    'bus': 822,
    'truck': 1000,
    'motorbike': 80,
    'plane': 285,
    'bicycle': 0,
    'van': 150
}

# Transformers imports
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model and tokenizer at import time (once)
# MODEL_NAME = "microsoft/DialoGPT-small"  # casual text conversational model
MODEL_NAME = "Qwen/Qwen2-1.5B-Instruct"
# MODEL_NAME = "Qwen/Qwen3-4B-Instruct-2507"  # Alternative text model more advanced but larger
print("Loading model... this may take a while on first run")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
device = "cuda" if torch.cuda.is_available() else "cpu"

# Async wrapper for generation to avoid blocking the event loop
async def generate_ai_reply(user_input: str) -> str:
    input_ids = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors="pt")
    input_ids = input_ids.to(device)
    def generate_blocking():
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                max_length=1500,
                pad_token_id=tokenizer.eos_token_id,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.8,
                num_return_sequences=1,
            )
            # The model's output includes the prompt; slice it out
            generated = outputs[0]
            reply_tokens = generated[input_ids.shape[-1]:]
            reply = tokenizer.decode(reply_tokens, skip_special_tokens=True)
            return reply
    reply = await asyncio.to_thread(generate_blocking)
    # fallback if empty
    if not reply:
        return "Sorry, I couldn't think of a SERIOUS reply just now... strange... Not so SERIOUS of me..."
    return reply

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
# command prefix 
bot = commands.Bot(command_prefix='$', description=description, intents=intents)
@bot.event

async def on_message(msg):
    # Ignore our own messages
    if msg.author == bot.user:
        return
    # If message is a command, let commands system handle it
    if msg.content.startswith('$'):
        await bot.process_commands(msg)
        return
    # Otherwise, try to generate AI reply
    try:
        # small guard: don't answer large attachments or empty messages
        if not msg.content or len(msg.content) > 1000:
            return
        reply = await generate_ai_reply(msg.content)
        # If reply exceeds Discord's 2000 character limit, save to a .txt and send as file
        if reply and len(reply) > 2000:
            fname = f"reply_{msg.id}.txt"
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(reply)
                await msg.channel.send("Reply too long — sending as a .txt file:", file=discord.File(fname))
            finally:
                try:
                    os.remove(fname)
                except Exception:
                    pass
        else:
            await msg.channel.send(reply)
    except Exception as e:
        # Don't crash the bot for a model error; log and fallback
        print("Error generating reply:", e)
        fallback = random.choice([
            "Hmm, I'm not sure I SERIOUSLY understood that, can you SERIOUSLY rephrase?",
            "I couldn't say a SERIOUSLY reply just now. Try again SERIOUSLY?",
        ])
        await msg.channel.send(fallback)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})') # type: ignore
    print('------')

# adding two numbers
@bot.command('add')
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)
# subtracting two numbers
@bot.command('min')
async def min(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left - right)
# multiplication two numbers
@bot.command('times')
async def times(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left*right)
# division two numbers
@bot.command('divide')
async def divide(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left/right)
# exp two numbers
@bot.command('exp')
async def exp(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left**right)
# mod
@bot.command('mod')
async def mod(ctx, left: int, right: int):
    """Adds two numbers together."""
    await  ctx.send(left%right)
# floor function
@bot.command('floor')
async def floor(ctx, number: float):
    """Returns the floor of a number."""
    await ctx.send(math.floor(number))
# ceiling function
@bot.command('celing')
async def ceil(ctx, number: float):
    """Returns the ceiling of a number."""
    await ctx.send(math.ceil(number))
# image classification 
@bot.command('classify')
async def classify(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            await attachment.save(f"./CV/{file_name}")
            label, score = get_class(model_path="keras_model.h5", image_path=f"./CV/{file_name}")
            percent = score * 100
            if percent >= 75:
                message = f" This image is classified as {label} with a confidence of {percent:.1f}%."
            elif percent >= 50:
                message = f" This image is classified as {label} with a confidence of {percent:.1f}%. I'm not very sure about this one."
            else:
                message = f" I'm not sure what this image is. The model thinks it might be {label} with a confidence of {percent:.1f}%."
            await ctx.send(message)
    else:
        await ctx.send("Please attach an image for classification.")

#Computer Vision count vehicles yessir
@bot.command()
async def deteksi(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            await attachment.save(f"./CV/{file_name}")
            
            # detection function me when count
            results = detect(input_image=f"./CV/{file_name}", output_image=f"./CV/{file_name}", model_path="yolov3.pt")
            
            # actually counting the detections
            if isinstance(results, list):
                counts = Counter(d['name'] for d in results)
                
                # vehicle emission count omg i hate ts
                total_emissions = 0
                for obj_name, count in counts.items():
                    # Check if detected object is in emission dictionary + count it
                    if obj_name in EMISSION_FACTORS:
                        total_emissions += count * EMISSION_FACTORS[obj_name]
                # ---------------------------------------

                msg = '\n'.join(f"{k}: {v}" for k, v in counts.items())
                
                total = sum(counts.values()) # <-- total object count
                
                
                if total_emissions > 5000:
                    temp = "High emissions detected! Bad for health."
                elif total_emissions > 2000:
                    temp = "Moderate emissions."
                else:
                    temp = "Normal emissions."
                    
                with open(f'./CV/{file_name}', 'rb') as f:
                    picture = discord.File(f)
                    
                await ctx.send(file=picture)
                await ctx.send(f"**Result:** {temp}")
                await ctx.send(f"**Object counts:**\n{msg}")
                await ctx.send(f"**Estimated Carbon Emissions:** {total_emissions} g CO2/km")   
    else:
        await ctx.send("You forgor to attach an image")

# # give local meme see python folder Data Science drive
@bot.command('meme')
async def meme(ctx):
    # try by your self 2 min
    img_name = random.choice(os.listdir('images'))
    with open(f'images/{img_name}', 'rb') as f:
        picture = discord.File(f)
 
    await ctx.send(file=picture)

# duck and dog API
def get_dog_image_url():
    url = 'https://random.dog/woof.json'
    res = requests.get(url)
    data = res.json()
    return data['url']
@bot.command('dog')
async def dog(ctx):
    '''Setiap kali permintaan dog (anjing) dipanggil, program memanggil fungsi get_dog_image_url'''
    image_url = get_dog_image_url()
    await ctx.send(image_url)

def get_duck_image_url():
    url = 'https://random-d.uk/api/random'
    res = requests.get(url)
    data = res.json()
    return data['url']
@bot.command('duck')
async def duck(ctx):
    '''Setiap kali permintaan duck (bebek) dipanggil, program memanggil fungsi get_duck_image_url'''
    image_url = get_duck_image_url()
    await ctx.send(image_url)

@bot.command('sentence')
async def tulis(ctx, *, my_string: str):
    with open('kalimat.txt', 'w', encoding='utf-8') as t:
        text = ""
        text += my_string
        t.write(text)

@bot.command('addsentence')
async def tambahkan(ctx, *, my_string: str):
    with open('kalimat.txt', 'a', encoding='utf-8') as t:
        text = "\n"
        text += my_string
        t.write(text)

@bot.command('baca')
async def baca(ctx):
    with open('kalimat.txt', 'r', encoding='utf-8') as t:
        document = t.read()
        await ctx.send(document)
        
# spamming word
@bot.command('spam')
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)
        
# password generator        
@bot.command('pw')
async def pw(ctx):
    await ctx.send(f'Kata sandi yang dihasilkan: {gen_pass(10)}')
@bot.command('bye')
async def bye(ctx):
    await ctx.send('\U0001f642')
# coinflip
@bot.command('coinflip')
async def coinflip(ctx):
    num = random.randint(1,2)
    if num == 1:
        await ctx.send('It is Head!')
    if num == 2:
        await ctx.send('It is Tail!')

# rolling dice
@bot.command('dice')
async def dice(ctx):
    nums = random.randint(1,6)
    if nums == 1:
        await ctx.send('It is 1!')
    elif nums == 2:
        await ctx.send('It is 2!')
    elif nums == 3:
        await ctx.send('It is 3!')
    elif nums == 4:
        await ctx.send('It is 4!')
    elif nums == 5:
        await ctx.send('It is 5!')
    elif nums == 6:
        await ctx.send('It is 6!')

# environment news or sumn
def get_weatherapi_weather(city):
    API_KEY = ' 3e648adbabad4abaa18130549251110'  # Replace with your WeatherAPI key
    url = f'http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={city}&lang=id'
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        location = data['location']['name']
        condition = data['current']['condition']['text']
        temp = data['current']['temp_c']
        return f"Cuaca di {location}: {condition}, Suhu: {temp}°C"
    else:
        return "Kota tidak ditemukan atau terjadi kesalahan."

@bot.command('weather')
async def weatherapi(ctx, *, city: str = "Jakarta"):
    """Menampilkan info cuaca menggunakan WeatherAPI."""
    info = get_weatherapi_weather(city)
    await ctx.send(info)


# welcome message
@bot.command('welcome')
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}') # type: ignore

#show local drive    
@bot.command('localdrive')
async def local_drive(ctx):
    try:
      folder_path = "./files"  # Replace with the actual folder path
      files = os.listdir(folder_path)
      file_list = "\n".join(files)
      await ctx.send(f"Files in the files folder:\n{file_list}")
    except FileNotFoundError:
      await ctx.send("Folder not found.") 
#show local file
@bot.command('showfile')
async def showfile(ctx, filename):
  """Sends a file as an attachment."""
  folder_path = "./files/"
  file_path = os.path.join(folder_path, filename)

  try:
    await ctx.send(file=discord.File(file_path))
  except FileNotFoundError:
    await ctx.send(f"File '{filename}' not found.")
# upload file to local computer
@bot.command('simpan')
async def simpan(ctx):
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file_name = attachment.filename
            # file_url = attachment.url  IF URL
            await attachment.save(f"./files/{file_name}")
            await ctx.send(f"Menyimpan {file_name}")
    else:
        await ctx.send("Anda lupa mengunggah :(")

bot.run('')


