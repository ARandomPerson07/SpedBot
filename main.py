import discord
import os
import random
from replit import db
from uptime import keep_alive
from discord.ext import commands

client = discord.Client()
speed_state = False

speed_d = {}
game = discord.Game("something, probably")
bot = commands.Bot(command_prefix = "_")
res_dict = {"I":"Ineffective","E":"Endured",
            "N":"Normal","W":"Weak", "F":"Fatal"}

if 'char_dict' not in db.keys():
  char_dict = {}
  db['char_dict']=char_dict

class character:
  def __init__(self, name = 'you forgot the name, congrats!',
              strength = 0, dex = 0, wit = 0, cha = 0, 
              s_res = 'Fatal', p_res = 'Fatal', b_res = 'Fatal', passive = "None"):
        self.name = name
        self.str = strength
        self.dex = dex
        self.wit = wit
        self.cha = cha
        self.s_res = s_res
        self.p_res = p_res
        self.b_res = b_res

  def stats(self):
    'Returns a discord embed with the character\'s stats'
    embed = discord.Embed(Title = f"{self.name}'s Stats",
                          colour = 0x13E8AE )
    embed.add_field(name = "Stats",
                    value = f"STR: {self.str}\nDEX: {self.dex} \nWIT: {self.wit}\
                    \nCHA: {self.cha}")
    embed.add_field(name =  "Resists",
                    value = f"Slash: {self.s_res}\nPierce: {self.p_res}\n\
                    Blunt:{self.b_res}")
    return embed

@bot.command(name = 'reg', help = 'Syntax: _reg [name] [S/W/D/C] [S/P/B]\nAccepted Resists are I/E/N/W/F\n\n e.g. _reg Adam 0/0/0/0 F/F/F')
async def register(ctx, name, stats, resists):
  stat_list = stats.split('/')
  if len(stat_list)!=4:
    await ctx.send("Please provide 4 stats in S/D/W/C format")
    return
  res_list = resists.split('/')
  if len(res_list)!=3:
    await ctx.send("Please provide the three resistances in S/P/B format")
    return
  globals()[name] = character(name,stat_list[0],stat_list[1],stat_list[2],stat_list[3],
            res_list[0],res_list[1],res_list[2])
  char_dict[name] = globals()[name]
  db['char_dict'] = char_dict
  


@client.event
async def on_connect():
    print('Successfully Logged In')


@client.event
async def on_ready():
    print('Bot ready')
    await client.change_presence(status = discord.Status.online, activity = game)

@client.event
async def on_message(message):

    global speed_state
    global speed_d

    if message.author != client.user and '_' in message.content:

        #_speed command
        if '_speed' in message.content:
            print('detected _speed command')

            if not speed_state:
                print('opening speed state')
                await message.channel.send(
                    'Awaiting speed rolls! Type _speed again to close speed rolls!'
                )
                speed_state = True
                print(speed_state)
                speed_d = {}

            elif speed_state:
                print('closing speed state')
                speed_state = False
                s_dict = dict(sorted(speed_d.items(),
                                     key=lambda item: item[1], reverse = True))
                speed_list = s_dict.keys()
                speed_message = "**"
                for item in speed_list:
                    speed_message = speed_message + item + " — "

                if speed_message:
                    await message.channel.send(speed_message + "**")
                speed_d = {}


        #_set command
        if speed_state:
            print('speedstate detected true')
            if '_set' in message.content:
                print('detected _set command')
                await message.add_reaction('✅')
                temp_list = message.content.split()
                print(f'temp_list updated to {temp_list}')

                if len(temp_list) < 3:
                    await message.channel.send(
                        'Syntax Error! Please use _set [roll] [name]')
                    return
                elif len(temp_list) == 3:
                    s_inputs = temp_list[1].split(',')
                    t_inputs = temp_list[2].split(',')
                    if len(s_inputs)!=len(t_inputs):
                      print("Please enter the same number of speeds and characters!")
                    for i,character in enumerate(t_inputs):
                      speed_d[t_inputs[i]] = int(s_inputs[i])+random.randint(0,100)/1000
    await bot.process_commands(message)

@client.event
async def on_disconnect():
    print('Exited successfully')

keep_alive()
client.run(os.environ['token'])
