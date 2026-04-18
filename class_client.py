#Kodland-Bot(client class)
import discord
# local own library
from bot_logic import gen_pass,coinflip,roll_dice,bananas_made
# Variabel intents menyimpan hak istimewa bot
intents = discord.Intents.default()
# Mengaktifkan hak istimewa message-reading
intents.message_content = True
# Membuat bot di variabel klien dan mentransfernya hak istimewa
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Kita telah masuk sebagai {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$hi'):
        await message.channel.send("hello there!")
    elif message.content.startswith('$bye'):
        await message.channel.send("\U0001f642")
    elif message.content.startswith('pass'):
        await message.channel.send(f"Kata sandi yang dihasilkan adalah {gen_pass(10)}")
    elif message.content.startswith('coin'):
        await message.channel.send(f"Koin yang dihasilkan adalah {coinflip()}")
    elif message.content.startswith('dice'):
        await message.channel.send(f"Dadu yang dihasilkan adalah {roll_dice()}")
    elif message.content.startswith('bananas?'):
        await message.channel.send(f"Bananas made today, {bananas_made()}")
@client.event    
async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)
        await guild.system_channel.send("try to type $halo or $bye or pass")

client.run("")
