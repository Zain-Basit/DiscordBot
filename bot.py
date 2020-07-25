# bot.py
import os
import random
import discord

from dotenv import load_dotenv
from discord.ext import commands
from lor_deckcodes import LoRDeck, CardCodeAndCount
from twisted_fate import Deck

load_dotenv() # This library loads env vars from .env files into the shell

TOKEN = os.getenv('DISCORD_TOKEN') # DISCORD_TOKEN is an env variable being pulled from the .env file, not committed to the repo
# GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='-')
# client = discord.Client()

# @client.event
@bot.event
async def on_ready():
    
    # for guild in client.guilds: # This basically checks through the name of the servers the bot is in, and prints the one that is defined as the main server
    #     if guild.name == GUILD:
    #         break

    # guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    # This line is the same as the for-loop above, it looks through the servers until it finds an element that matches the predicate (lambda g)

    # guild = discord.utils.get(client.guilds, name=GUILD)
    # This line is the same as both of the above statements, it looks through the servers until it finds an element that matches the GUILD name
    """
    get() takes the iterable and some keyword arguments. The keyword arguments represent attributes of the elements in the iterable that must all
    be satisfied for get() to return the element.
    Technical Detail: Under the hood, get() actually uses the attrs keyword arguments to build a predicate, which it then uses to call find().
    """

    game = discord.Game("a fair game.") # This sets the bot's status, and since I'm running with a Twisted Fate theme, it makes sense for him to play some cards! 
    await bot.change_presence(activity=game)

    print(
            f'{bot.user.name} has connected to Discord!'
        #   f'{client.user} has connected to the following server:\n'
        #   f'{guild.name} (id: {guild.id})'
    )
        
@bot.command(name='tf', help='Responds with random Twisted Fate quotes.')
async def twisted_fate(ctx):
    twisted_fate_quotes = ['Never lost a fair game...or played one.',
                        'I\'m always up for a round or two.',
                        'Only fools play the hand they\'re dealt.',
                        'All or nothin\'']

    response = random.choice(twisted_fate_quotes)
    await ctx.send(response)
    
@bot.command(name='deckcode', help='Will take a deckcode and return display it')
async def deckcode(ctx, code: str):

    deck = LoRDeck.from_deckcode(code) # Decoding the deckcode

    deck = list(deck) # This is a list that contains how many copies of a card are in the deck, and the card code. Ex: 3:01PZ016, so there are 3 copies, 

    # First lets break up the deck into it's different regions
    card = deck[0]
    region_1 = [card[4:6]]
    region_2 = []

    for card in deck:
        
        region = card[4:6] # This gives us the region only, and ignores the # of copies
        
        if region in region_1:
            region_1.append(card)
        else:
            region_2.append(card)
        
    card = region_2[0]
    region_2.insert(0, card[4:6])

    embed_deck = discord.Embed(
        title='Decklist',
        description = f'Regions: {what_region(region_1[0])} and {what_region(region_2[0])}',
        colour = discord.Colour.red()
    )

    ############### Need to figure out numbering of cards, and costs, and names now

    deck = Deck.decode(code) # Using the twisted_fate library to reformat the deck, it is a list with Card Costs and Names
    deck = deck.cards # Ex: Card(01NX020, Name: Draven, Cost: 3)

    # Converting the region lists into region dictionaries

    r1 = region_1.pop(0)
    r2 = region_2.pop(0)

    region1_dict = convert_dict(region_1)
    region2_dict = convert_dict(region_2)
    
    region_1.insert(0, r1)
    region_2.insert(0, r2)

    region1_cards = ""
    region2_cards = ""
    region1_costs = ""
    region2_costs = ""

    for card in deck:
        
        card_code = card.cardCode
        if card.cardCode[2:4] in region_1: 
            region1_cards += "**" + region1_dict[card_code] + "** " + card.name + "\n" #+ " **Cost: " + str(card.cost) + "**\n"           
            region1_costs += "**Cost: " + str(card.cost) + "**\n"

        elif card.cardCode[2:4] in region_2: 
            region2_cards += "**" + region2_dict[card_code] + "** " + card.name + "\n" #" **Cost: " + str(card.cost) + "**\n"
            region2_costs += "**Cost: " + str(card.cost) + "**\n"

    champs = (Deck.decode(code)).champions()
    champions = ""
    for champ in champs:
        champions += champ + "/"
    
    if champions == "":
        champions = "There are no champions in the deck"

    embed_deck.add_field(name='Champions', value=champions, inline=False)
    embed_deck.add_field(name=f'{what_region(region_1[0])} Cards:', value=region1_cards, inline=True)
    embed_deck.add_field(name='Cost:', value=region1_costs, inline=True)
    embed_deck.add_field(name='- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -', value='\u200b', inline=False)
    embed_deck.add_field(name=f'{what_region(region_2[0])} Cards:', value=region2_cards, inline=True)
    embed_deck.add_field(name='Cost:', value=region2_costs, inline=True)

    await ctx.send(embed=embed_deck)

"""
Takes a list in the format ['Int 1-3:Code', ..., ...] and puts it into a dictionary
"""
def convert_dict(list_to_convert: list) -> dict:

    new_dict = {}

    for set in list_to_convert:
        parts = set.split(':')
        new_dict[parts[1]] = parts[0]

    return new_dict

"""
Takes in a region code and returns the full string version
"""
def what_region(region_code: str) -> str:

    region_dictionary = {
        'DE': 'Demacia',
        'IO' : 'Ionia',
        'NX' : 'Noxus',
        'PZ' : 'Piltover & Zaun',
        'SI' : 'Shadow Isles',
        'FR' : 'Freljord',
        'BW' : 'Bilgewater',
    }

    return region_dictionary[region_code]

@bot.command(name='hello', help='Responds with a hello message, and a picture of a friendly robot.')
async def hello(ctx):
    await ctx.send('Hello to you too, friend!', file=discord.File('path.jpg'))

@bot.command(name='roll', help='Simulates rolling dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides+1)))
        for _ in range(number_of_dice)
    ]

    await ctx.send(', '.join(dice))

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled Message: {args[0]}]n')
        else:
            raise

@bot.event
async def on_member_join(member): # This function handles what happens when someone joins the server
    await member.create_dm() # await suspends the execution of the surrounding coroutine until the execution of each coroutine has finished.
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to the server!'
    )

# client.run(TOKEN) # Created a client and the ready event handler, which is called once the client is ready for any other action
bot.run(TOKEN)
