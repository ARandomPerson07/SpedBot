import discord
import os
import random
from replit import db
from uptime import keep_alive
from discord.ext import commands
import asyncio
import math
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('dark_background')

from collections import Counter
#initialise variables
speed_state = False
speed_d = {}
game = discord.Game("something, probably")
bot = commands.Bot(command_prefix = "_")
res_dict = {"I":"Ineffective","E":"Endured",
            "N":"Normal","W":"Weak", "F":"Fatal"}
char_list = []


class character:
  def __init__(self, cha_name = 'you forgot the name, congrats!',
              strength = 0, dex = 0, wit = 0, cha = 0, 
              s_res = 'Fatal', p_res = 'Fatal', b_res = 'Fatal', passive = "None", max_hp = 30, hp = 30, max_sr = 15, sr = 0):
        self.name = cha_name
        self.str = strength
        self.dex = dex
        self.wit = wit
        self.cha = cha
        self.s_res = s_res
        self.p_res = p_res
        self.b_res = b_res
        self.mhp = max_hp
        self.hp = hp
        self.msr = math.floor(max_hp/2)
        self.sr = sr
 
  def stats(self):
    'Returns a discord embed with the character\'s stats'
    embed = discord.Embed(Title = f"{self.name}'s Stats",
                          colour = 0x13E8AE, description = f"{self.name}'s Stats")
    embed.add_field(name = "Resources", value = f"HP:{self.hp}/{self.mhp}\nSR:{self.sr}/{self.msr}")
    embed.add_field(name = "Stats",
                    value = f"STR: {self.str}\nDEX: {self.dex} \nWIT: {self.wit}\
                    \nCHA: {self.cha}")
    embed.add_field(name =  "Resists",
                    value = f"Slash: {self.s_res}\nPierce: {self.p_res}\nBlunt: {self.b_res}")
    return embed

#initialise all chara instances
for v in db.values():
  try:
      print('found a dictionary')
      a = v['name']
      globals()[a] = character(v['name'],v['stats'][0],v['stats'][1],v['stats'][2],v['stats'][3],v['res'][0],v['res'][1],v['res'][2],
      "None",v['resources'][0],v['resources'][1],v['resources'][2],v['resources'][3])
      print('created character',v['name'])
      char_list.append(a)
  except:
    pass


#opening log
@bot.event
async def on_connect():
    print('Successfully Logged In')


@bot.event
async def on_ready():
    print('Bot ready')
    await bot.change_presence(status = discord.Status.online, activity = game)

#_update command
@bot.command(aliases=['update','ud','upd','up'], 
              help = "Update the current stats of your character.\n\n Valid arguments: STR/DEX/WIT/CHA/res/hp/mhp/sr/msr\n\nExamples:\n\n_up dex 20\n_up res F/F/F")
async def update_char(ctx,char,rstat,value):
  stat = rstat.lower()
  if char not in char_list:
    await ctx.send('Character not found!')
    return
  if stat not in ['str','dex','wit','cha','res','mhp','hp','sr','msr']:
    await ctx.send('Invalid argument!')
    return
  nval = int(value)
  if stat =="str":
    globals()[char].str = nval
    db[char]['stats'][0]= nval
  if stat =="dex":
    globals()[char].str = nval
    db[char]['stats'][1]= nval
  if stat =="wit":
    globals()[char].str = nval
    db[char]['stats'][2]= nval
  if stat =="cha":
    globals()[char].str = nval
    db[char]['stats'][3]= nval
  if stat == 'mhp':
    globals()[char].mhp = nval
    db[char]['resources'][0] = nval
    globals()[char].msr = math.floor(nval/2)
    db[char]['resources'][2] =math.floor(nval/2)
  if stat == 'hp':
    globals()[char].hp = nval
    db[char]['resources'][0] = nval
  if stat == 'sr':
    globals()[char].sr = nval
    db[char]['resources'][3] = nval
  if stat == "res":
    res_list = value.split("/")
    res_list = [res_dict[x] for x in res_list]
    db[char]['res'] = res_list
    globals()[char].sres = res_list[0]
    globals()[char].pres = res_list[1]
    globals()[char].bres = res_list[2]
    

  await ctx.message.add_reaction('✅')


#_char command
@bot.command(aliases=['characters','char','chars','charas'], help = 'Displays all the currently registered characters')
async def list_characters(ctx):
  char_str  = ""
  for item in char_list:
    char_str=char_str+item+"\n"
  embed = discord.Embed()
  embed.add_field(name = "Characters",value = char_str)
  await ctx.send(embed= embed)

#_roll command
@bot.command(name = 'roll')
async def roll(ctx,*dice):
  results = []
  for item in dice:
    typedice = item.split('d')
    typedice = [x for x in typedice if x!='']
    print(typedice)
    typedice = [int(x) for x in typedice]
    if len(typedice)==1:
      result = random.randint(1,int(typedice[0]))
      results.append(f'd{typedice[0]} = **{result}**')
    else:
      x = 0
      subresults = []
      while x < typedice[0]:
        subresults.append(random.randint(1,typedice[1]))
        x+=1
      str_sub = ", ".join([str(x) for x in subresults])
      results.append(f'{typedice[0]}d{typedice[1]} = [{str_sub}] = **{sum(subresults)}**')
  flat_results = "\n".join(results)
  await ctx.send(flat_results)

#_rollstat command
@bot.command(name = 'rollstat', aliases = ['rs'] )
async def rollstat(ctx,*dice):
  await ctx.message.add_reaction('✅')
  for item in dice:
    typedice = item.split('d')
    typedice = [x for x in typedice if x!='']
    typedice = [int(x) for x in typedice]
    if len(typedice)==1:
      await ctx.send('A single dice is always equally likely on all sides')
    else:
      subresults = []
      #determine roll number based on dice complexity
      dicecomplexity = typedice[0]*typedice[1]
#      dicecomplexity2 = dicecomplexity*typedice[0]
#      rollnum = math.floor(9000000/dicecomplexity2)
      rollnum = 200000
      x = np.arange(1,rollnum)
      for element in x:
        #roll the dice as requested, add their sum to a list
        tempresults = []
        dice_count = 0
        while dice_count<typedice[0]:
          dice_count+=1
          tempresults.append(random.randint(1,typedice[1]))
        subresults.append(sum(tempresults))
      results = Counter(subresults)
      for dice_sum in results.keys():
        results[dice_sum] = results[dice_sum]/rollnum*100

      maxprob = max(results.values())

      resultkeytemp = list(results.keys())
      for key in resultkeytemp:
        if results[key]<maxprob*0.05:
          del results[key]
      resultssort = sorted(results.items())
      resultkeys = [x[0] for x in resultssort]
      resultvalues = [x[1] for x in resultssort]
      
      print(resultkeys)
    
      height = dicecomplexity*0.66
      scaler = 0.8+height*0.015
      fig = plt.figure(figsize = (9*(0.8+height*0.015),height), dpi = 75)
      ax = fig.add_subplot(111)
      ax.barh(resultkeys,resultvalues)
      
      ax.set_yticks(np.arange(min(resultkeys),max(resultkeys)+1))
      ax.set_ylabel("Roll Sum", size = 48*scaler)
      ax.set_xlabel("Probability(%)", size = 48*scaler)
      plt.yticks(fontsize = 36*scaler)
      fig.tight_layout()
      fig.savefig('test.png')
      await ctx.send(file = discord.File('test.png'))

      #plt.savefig('images/graph.png', transparent=True)
     # plt.close(fig)
    #  with open('images/graph.png', 'rb') as f:
   #     file = io.BytesIO(f.read())
        
  #    image = discord.File(file, filename='graph.png')
 #     embed.set_image(url=f'attachment://graph.png')

#      await ctx.send(file=image, embed=embed)
#      to_send = ""
#      for key,value in sorted(results.items()):
#        to_send = to_send + str(key)+ " | "+ str(value)+"\n"
#      await ctx.send(to_send)

      
        

      

#_reg command
@bot.command(name = 'reg', help = 'Syntax: _reg [name] [S/W/D/C] [S/P/B] [Max HP]\nAccepted Resists are I/E/N/W/F\n\n e.g. _reg Adam 0/0/0/0 F/F/F')
async def register(ctx, arg_name = 'Adam', stats = '0/0/0/0', resists="F/F/F", mhp = 30):
  print('_reg detected')
  stat_list = stats.split('/')
  stat_list = [int(x) for x in stat_list]
  if len(stat_list)!=4:
    await ctx.send("Please provide 4 stats in S/D/W/C format")
    return
  res_list = resists.split('/')
  if len(res_list)!=3:
    await ctx.send("Please provide the three resistances in S/P/B format")
    return
  mhp = int(mhp)
  upd_res = [res_dict[x] for x in res_list]
  msr = math.floor(mhp/2)
  #the following line follows mhp/hp/msr/sr conventions
  resources = [mhp,mhp,msr,msr]
  #saves character metadata to db
  db[arg_name] = {'name':arg_name, 'stats':stat_list,'res':upd_res, 'resources':resources}
  #creates chara in the current runtime
  globals()[arg_name] = character(arg_name,stat_list[0],stat_list[1],                       stat_list[2],stat_list[3],upd_res[0],upd_res                        [1],upd_res[2],"None",mhp,mhp,
                        msr)
  await ctx.message.add_reaction('✅')
  if arg_name not in char_list:
    char_list.append(arg_name)
  print(db.keys(), [type(x) for x in db.values()])


#_stats command
@bot.command(name = 'stats')
async def display_stats(ctx, name):
  try:
    if type(globals()[name])==character:
      await ctx.send(embed = globals()[name].stats())
    else:
      await ctx.send('Character not found!')
  except KeyError:
    await ctx.send('Character not found!')

#@bot.command(name = 'purge')
#async def purge(ctx):
#  for key in db.keys():
#    del db[key]
#    await ctx.send(f'Deleted {key}')

#custom commands
@bot.event
async def on_message(message):

    global speed_state
    global speed_d

    if message.content == "hi":
      print('hi detected')
      await message.add_reaction('👀')

    if message.author != bot.user and '_' in message.content:
        content = message.content
        author = message.author
        channel = message.channel

        #_speed command
        if '_speed' in content:
            print('detected _speed command')
            if not speed_state:
                print('opening speed state')
                await channel.send(
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
                    await channel.send(speed_message + "**")
                speed_d = {}

        #_del command
        if content.startswith("_del"):
          print('_del command detected')
          m_list = content.split()
          if m_list[1] in db.keys():
            await channel.send(f"Are you sure you want to delete {m_list[1]} [y/n]?")

            def check(response):
              return response.author == author and (response.content =='y' or response.content =='n')
            try:
              response = await bot.wait_for('message',check = check, timeout = 30)
              if response.content.lower()==('y'):
                del db[m_list[1]]
                globals()[m_list[1]]= None
                char_list.remove(m_list[1])
                await channel.send(f"{m_list[1]} has been deleted...")
              elif response.content.lower()==('n'):
                await channel.send(f"{m_list[1]} lives to see another day")
            except asyncio.TimeoutError:
              channel.send('Time\'s up! Deletion cancelled')
          else:
            await channel.send('Character not found!')

        #_set command
        if speed_state:
            print('speedstate detected true')
            if '_set' in content:
                print('detected _set command')
                await message.add_reaction('✅')
                temp_list = content.split()
                temp_list = [temp_list[0],temp_list[1]," ".join(temp_list[2:])]
                print(f'temp_list updated to {temp_list}')

                if len(temp_list) < 3:
                    await channel.send(
                        'Syntax Error! Please use _set [roll] [name]')
                    return
                elif len(temp_list) == 3:
                    #speed and target
                    s_inputs = temp_list[1].split(',')
                    t_inputs = temp_list[2].split(',')
                    if len(s_inputs)!=len(t_inputs):
                      await channel.send("Please enter the same number of speeds and characters!")
                    for i,character in enumerate(t_inputs):
                      speed_d[t_inputs[i]] = int(s_inputs[i])+random.randint(0,100)/1000 

    await bot.process_commands(message)

@bot.event
async def on_disconnect():
    print('Exited successfully')


keep_alive()
bot.run(os.environ['token'])
