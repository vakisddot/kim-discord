from discord import Intents
from discord.ext import commands
from random import randint
from KimExtras import *
import config
import sqlite3

# API Configuration
intents = Intents.default()
intents.members = True
client = commands.Bot(command_prefix="/kim ", intents=intents)
client.remove_command("help")

# File names
tokenFile = "token.txt"
helpMessageFile = "HelpMessage.txt"

db = sqlite3.connect(config.dbName)

MAX_DESC_LENGTH = 255
MAX_WORD_LENGTH = 95


@client.event
async def on_guild_join(guild):
    members = []
    for member in guild.members:
        # If member isn't the bot itself
        if member.id != 854075604035305542:
            members.append(member.id)

    print(f"Joined new server: {guild.id}, {guild.name}")
    config.addNewServer(guild.id, guild.name, members)


@client.event
async def on_member_join(member):
    config.serverId = member.guild.id
    queryTemplate("insert", "users", "id", member.id)


@client.event
async def on_member_remove(member):
    config.serverId = member.guild.id
    queryTemplate("delete", "users", "id", member.id)


@client.event
async def on_message_edit(default, CTX):
    await on_message(CTX)


@client.event
async def on_message(CTX):
    # Makes sure that the bot doesn't interact with its own messages
    if CTX.author == client.user:
        return
    cur = db.cursor()

    # Gets server data
    cur.execute("SELECT * FROM servers WHERE id = ?;", (CTX.guild.id,))
    try:
        serverData = cur.fetchall()[0]
    except:
        await on_guild_join(CTX.guild)
        cur.execute("SELECT * FROM servers WHERE id = ?;", (CTX.guild.id,))
        serverData = cur.fetchall()[0]
    cur.execute("SELECT word FROM words WHERE serverId = ?;", (CTX.guild.id,))
    wordsData = config.fetchStrings(cur)
    cur.execute("SELECT phrase FROM phrases WHERE serverId = ?;", (CTX.guild.id,))
    phrasesData = config.fetchStrings(cur)
    cur.execute("SELECT description FROM descriptions WHERE serverId = ?;", (CTX.guild.id,))
    descriptionsData = config.fetchStrings(cur)
    cur.execute("SELECT swearCount FROM users WHERE serverId = ? AND id = ?;", (CTX.guild.id, CTX.author.id))

    # Sets current server data to python variables
    config.swearCount = cur.fetchall()[0][0]
    config.serverId = serverData[0]
    config.serverName = serverData[1]
    config.spoilerMode = serverData[2]
    config.canKick = serverData[3]
    config.swearThreshold = serverData[4]
    config.replyInDm = serverData[5]
    config.words = wordsData
    config.phrases = phrasesData
    config.descriptions = descriptionsData

    # Checks if there's a censored word
    characterMap = createCharacterMap(CTX.content, config.words)

    # Deletes message and sends reply
    if True in characterMap:
        # Deletes the user's message
        user = CTX.author
        await CTX.delete()

        await CTX.channel.send\
        (
            "\U0001F441 " +
            createDesc(str(CTX.author.name), config.descriptions[randint(0, len(config.descriptions) - 1)]) +
            "> " + createBotMessage(CTX.content, characterMap)
        )

        if config.swearThreshold > 0:
            queryTemplate("updateUser", "users", "swearCount", config.swearCount + 1, CTX.author.id)

            if config.swearCount >= config.swearThreshold * 0.60 and config.swearCount < config.swearThreshold:
                if config.canKick > 0:
                    await CTX.channel.send(f"> \U0001F6AB Warning! **{str(CTX.author.name)}** is close to reaching the profanity threshold!")
            elif config.swearCount >= config.swearThreshold:
                if config.canKick > 0:
                    await CTX.channel.send(f"> \U0001F6A8 **WARNING! {str(CTX.author.name)}** has reached the profanity threshold!")
                if config.canKick == 2:
                    try:
                        await user.kick(reason="Kicked by K.I.M. - Profanity threshold reached!")
                    except:
                        await CTX.channel.send("> *Couldn't kick user. Maybe you didn't give me permissions?*")
                    else:
                        await CTX.channel.send(f"> \U0001F6D1 User **{str(CTX.author.name)}** has been kicked.")
                elif config.canKick == 3:
                    try:
                        await user.ban(reason="Banned by K.I.M. - Profanity threshold reached!")
                    except:
                        await CTX.channel.send("> *Couldn't ban user. Maybe you didn't give me permissions?*")
                    else:
                        await CTX.channel.send(f"> \U0001F6D1 User **{str(CTX.author.name)}** has been banned.")

    await client.process_commands(CTX)


async def sanitized(CTX, STR):
    if '"' in STR or "'" in STR:
        await botMessage(CTX, "> \U0001F6D1 Warning! Don't use quotations in input!")
        return False
    return True

# Mini function that creates the list strings in those /kim *_list commands
def makeList(ELEMENTS):
    ls = []
    for i, element in enumerate(ELEMENTS):
        ls.append('> ' + str(i + 1) + ". " + element)
    return "\n".join(ls)


def queryTemplate(QUERY, TABLE, COLUMN, DATA, USERID=0):
    if QUERY not in ["insert", "delete", "update", "updateServer", "updateUser"]:
        print("Invalid query request")
        return
    curs = db.cursor()
    if QUERY == "insert":
        curs.execute('INSERT INTO "{}" (serverId, "{}") VALUES (?, ?);'
                    .format(TABLE.replace('"', '""'), COLUMN.replace('"', '""')), 
                    (config.serverId, DATA))
    elif QUERY == "delete":
        curs.execute('DELETE FROM "{}" WHERE serverId = ? AND "{}" = ?;'
                    .format(TABLE.replace('"', '""'), COLUMN.replace('"', '""')), 
                    (config.serverId, DATA))
    elif QUERY == "update":
        curs.execute('UPDATE "{}" SET "{}" = ? WHERE serverId = ?;'
                    .format(TABLE.replace('"', '""'), COLUMN.replace('"', '""')), 
                    (DATA, config.serverId))
    elif QUERY == "updateUser":
        curs.execute('UPDATE "{}" SET "{}" = ? WHERE serverId = ? AND id = ?;'
                    .format(TABLE.replace('"', '""'), COLUMN.replace('"', '""')), 
                    (DATA, config.serverId, USERID))
    elif QUERY == "updateServer":
        curs.execute('UPDATE "{}" SET "{}" = ? WHERE id = ?;'
                    .format(TABLE.replace('"', '""'), COLUMN.replace('"', '""')), 
                    (DATA, config.serverId))
    db.commit()
    curs.close()


# This generates bot replies to commands
async def botMessage(CTX, MSG):
    if config.replyInDm == 2:
        # Sends reply in DM
        channel = await CTX.author.create_dm()
        await channel.send(MSG)
    else:
        # Sends reply in text channel
        await CTX.send(MSG)
    
    # Deletes the user's command
    if config.replyInDm == 1:
        await CTX.message.delete()


@client.command(brief="Use this to add a filter word")
@commands.has_permissions(manage_messages=True)
async def w_add(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = sensitive(arg)
    print(arg)

    if not arg or len(arg) < 2:
        await botMessage(ctx, "> Missing or invalid arguments!")
    elif len(arg) > MAX_WORD_LENGTH:
        await botMessage(ctx, "> Word is too long!")
    elif arg not in config.words:
        queryTemplate("insert", "words", "word", arg)
        await botMessage(ctx, "> \N{THUMBS UP SIGN}  Added new filter word!")
    else:
        await botMessage(ctx, "> Word has already been added!")


@client.command(brief="Use this to remove a filter word")
@commands.has_permissions(manage_messages=True)
async def w_del(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = arg.strip()

    for i, word in enumerate(config.words):
        if sensitive(word) == sensitive(arg) or arg == str(i + 1):
            queryTemplate("delete", "words", "word", sensitive(word))
            await botMessage(ctx, "> \N{THUMBS UP SIGN}  Removed filter word.")
            break
        elif i == len(config.words) - 1:
            await botMessage(ctx, "> Couldn't find word.")


@client.command(brief="Lists all filter words")
@commands.has_permissions(manage_messages=True)
async def w_list(ctx):
    await botMessage(ctx,
        "\U0001F51E Filter words list for this server:\n"
        "*(Note: You can delete these using their number index,"
        "e.g., /kim w_del 4)*")

    await botMessage(ctx, makeList(config.words))


@client.command(brief="Adds a replacement phrase")
@commands.has_permissions(manage_messages=True)
async def repl_add(ctx, *args):
    newRepl = " ".join(args).strip()

    if len(newRepl) > MAX_WORD_LENGTH:
        await botMessage(ctx, "> Phrase is too long!")
    elif newRepl not in config.phrases:
        queryTemplate("insert", "phrases", "phrase", newRepl)
        await botMessage(ctx, "> \N{THUMBS UP SIGN}  Added new replacement phrase!")
    else:
        await botMessage(ctx, "> Phrase has already been added!")


@client.command(brief="Removes a replacement phrase")
@commands.has_permissions(manage_messages=True)
async def repl_del(ctx, *args):
    deleteRepl = " ".join(args).strip()

    for i, phrase in enumerate(config.phrases):
        if len(config.phrases) < 2:
            await botMessage(ctx, "> \U0001F6D1 There must be at least 2 phrases!")
            break
        elif phrase == deleteRepl or deleteRepl == str(i + 1):
            queryTemplate("delete", "phrases", "phrase", phrase)
            await botMessage(ctx, '> \N{THUMBS UP SIGN}  Deleted replacement phrase: ' + '*' + deleteRepl + '*')
            break
        elif i == len(config.phrases) - 1:
            await botMessage(ctx, "> Couldn't find replacement phrase.")


@client.command(brief="Lists all replacement phrases")
@commands.has_permissions(manage_messages=True)
async def repl_list(ctx):
    await botMessage(ctx, 
        "\U0001F4CC Replacement phrases for this server:\n"
        "*(Note: You can remove these using their number index, "
        "e.g., /kim repl_del 3)*")

    await botMessage(ctx, makeList(config.phrases))


@client.command(brief="Adds a new description")
@commands.has_permissions(manage_messages=True)
async def desc_add(ctx, *args):
    # This checks if the last character of the description is a punctuation
    if args[-1][-1] in config.sensPunctuations:
        newArgs = ' '.join(args)
        newDescription = newArgs[0:len(newArgs) - 1].strip()
    else:
        newDescription = ' '.join(args).strip()

    if len(newDescription) > MAX_DESC_LENGTH:
        await botMessage(ctx, "> Description is too long!")
    elif newDescription[0] == "#":
        await botMessage(ctx, "> \U0001F6D1 Description can't start with a '#'!")
    elif newDescription not in config.descriptions:
        queryTemplate("insert", "descriptions", "description", newDescription)
        await botMessage(ctx, "> \N{THUMBS UP SIGN}  New description added: " + '*' + newDescription + '*')
    else:
        await botMessage(ctx, "> Description already added.")


@client.command(brief="Removes a description")
@commands.has_permissions(manage_messages=True)
async def desc_del(ctx, *args):
    deleteDesc = ' '.join(args).strip()

    for i, desc in enumerate(config.descriptions):
        if len(config.descriptions) < 2:
            await botMessage(ctx, "> \U0001F6D1 There must be at least 2 descriptions!")
            break
        elif desc == deleteDesc or deleteDesc == str(i + 1):
            queryTemplate("delete", "descriptions", "description", desc)
            await botMessage(ctx, '> \N{THUMBS UP SIGN}  Deleted description: ' + '*' + deleteDesc + '*')
            break
        elif i == len(config.descriptions) - 1:
            await botMessage(ctx, "> Couldn't find description.")


@client.command(brief="Lists all descriptions")
@commands.has_permissions(manage_messages=True)
async def desc_list(ctx):
    await botMessage(ctx, 
        "\U0001F4D6 Descriptions for this server:\n"
        "*(Note: You can remove these using their number index, "
        "e.g., /kim desc_del 6)*")

    await botMessage(ctx, makeList(config.descriptions))


@client.command(brief="Filter mode")
@commands.has_permissions(manage_messages=True)
async def filter_mode(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = arg.strip()

    if arg not in ["0", "1"]:
        await botMessage(ctx, "> \U0001F6D1 Invalid arguments!")
    else:
        queryTemplate("updateServer", "servers", "spoilerMode", arg)
        if arg == "1":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Filtered words can now be revealed!")
        else: 
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Filtered words will now be replaced with a random phrase!")


@client.command(brief="Choose where the bot should reply")
@commands.has_permissions(manage_messages=True)
async def dm(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = arg.strip()

    if arg not in ["0", "1", "2"]:
        await botMessage(ctx, "> \U0001F6D1 Invalid arguments!")
    else:
        queryTemplate("updateServer", "servers", "replyInDm", arg)
        if arg == "2":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will now reply in DMs!")
        else: 
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will now reply in text channel!")


@client.command(brief="Choose where the bot should reply")
@commands.has_permissions(manage_messages=True)
async def can_kick(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = arg.strip()

    if arg not in ["0", "1", "2", "3"]:
        await botMessage(ctx, "> \U0001F6D1 Invalid arguments!")
    else:
        queryTemplate("updateServer", "servers", "canKick", arg)
        if arg == "0":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will no longer warn users.")
        elif arg == "1":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will now just warn users who have reached the threshold.")
        elif arg == "2":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will now kick all users who have reached the threshold!")
        else: 
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will now **ban** all users who have reached the threshold!")


@client.command(brief="Choose where the bot should reply")
@commands.has_permissions(manage_messages=True)
async def threshold(ctx, arg):
    if not await sanitized(ctx, arg):
        return

    arg = arg.strip()

    if arg not in [str(i) for i in range(255)]:
        await botMessage(ctx, "> \U0001F6D1 Invalid arguments! **[0-255]**")
    else:
        queryTemplate("updateServer", "servers", "swearThreshold", arg)
        if arg == "0":
            await botMessage(ctx, "> \N{THUMBS UP SIGN} Bot will no longer keep track of users.")
            queryTemplate("update", "users", "swearCount", 0)
        else:
            await botMessage(ctx, f"> \N{THUMBS UP SIGN} Bot will now keep track of users! New threshold has been set. ({arg})")
            


@client.command()
@commands.has_permissions(manage_messages=True)
async def help(ctx, arg="0"):
    if not await sanitized(ctx, arg):
        return
    
    arg = int(arg.strip())

    sendCommand = "\n\n> **`/kim help`** to go back"
    fName = "KimHelpMessages/"

    if arg not in range(1, 6):
        fName += "HelpMessage.txt"
        sendCommand = ""
    elif arg == 1:
        fName += "Words.txt"
    elif arg == 2:
        fName += "Phrases.txt"
    elif arg == 3:
        fName += "Descriptions.txt"
    elif arg == 4:
        fName += "Moderation.txt"
    elif arg == 5:
        fName += "Extras.txt"

    with open(fName, "r", encoding='utf-8') as file:
        lines = [line.rstrip() for line in file]

    await botMessage(ctx, "\n".join(lines) + sendCommand)


try:
    f = open(tokenFile, "r")
except:
    print("Couldn't find token file. New file created. Please re-launch once you've entered your token!")
    fCreate = open(tokenFile, "x")
    fCreate.close()
    f = open(tokenFile, "r")

try:
    client.run(f.read())
except:
    print("Error: Couldn't read token in token file!")
