import discord
import os
import random
from replit import db
from uptime import keep_alive

client = discord.Client()
speed_state = False

speed_d = {}
game = discord.Game("something, probably")

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

    if message.author != client.user:

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


@client.event
async def on_disconnect():
    print('Exited successfully')

keep_alive()
client.run(os.environ['token'])
