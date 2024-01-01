import discord
from discord.ext import commands, tasks


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='<', intents=intents)

# Replace this with the ID of the specific user allowed to use the commands
allowed_user_id = 1179769080316698684

# Anti-spam settings
SPAM_COOLDOWN = 5  # Cooldown period in seconds
SPAM_THRESHOLD = 5  # Maximum number of messages within the cooldown period

# Dictionary to track user messages
user_messages = {}

@bot.event
async def on_message(message):
    # Check if the user is the allowed user or has a role higher than the bot's role
    if message.author.id != allowed_user_id and not any(role > bot.user.top_role for role in message.author.roles):
        # Anti-spam handling
        if message.author.id in user_messages:
            # Check if the user has sent too many messages within the cooldown period
            if len(user_messages[message.author.id]) >= SPAM_THRESHOLD:
                await message.channel.send("You're sending messages too quickly. Slow down!")

            # Check if the time since the last message is within the cooldown period
            elif message.created_at.timestamp() - user_messages[message.author.id][-1].created_at.timestamp() < SPAM_COOLDOWN:
                await message.channel.send("You're sending messages too quickly. Slow down!")

        # Update user message history
        if message.author.id not in user_messages:
            user_messages[message.author.id] = []

        user_messages[message.author.id].append(message)

        # Remove old messages from the user's history
        user_messages[message.author.id] = [m for m in user_messages[message.author.id] if
                                             message.created_at.timestamp() - m.created_at.timestamp() <= SPAM_COOLDOWN]

    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await delete_suspicious_roles()
    change_status.start()

@tasks.loop(seconds=30)  # Change status every 30 seconds (adjust as needed)
async def change_status():
    new_status = f"Caso box | Happy new year!"
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=new_status))

async def delete_suspicious_roles():
    for guild in bot.guilds:
        for role in guild.roles:
            if role.permissions.administrator and role.position < guild.me.top_role.position:
                try:
                    await role.delete()
                    print(f"Deleted suspicious role: {role.name} in {guild.name}")
                except discord.Forbidden:
                    print(f"Insufficient permissions to delete role: {role.name} in {guild.name}")
                except discord.HTTPException as e:
                    print(f"An error occurred: {e}")

@bot.command(name='lock')
async def lock(ctx):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send('Channel has been locked.🔒')
    else:
        await ctx.send('You are not allowed to use this.')

@bot.command(name='unlock')
async def unlock(ctx):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send('Channel has been unlocked.🔓')
    else:
        await ctx.send('You are not allowed to use this.')

@bot.command(name='kick')
async def kick(ctx, member: discord.Member, *, reason=None):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member} for: {reason}')
    else:
        await ctx.send('You are not allowed to use this.')

@bot.command(name='ban')
async def ban(ctx, member: discord.Member, *, reason=None):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member} for: {reason}')
    else:
        await ctx.send('You are not allowed to use this.')

@bot.command(name='mute')
async def mute(ctx, member: discord.Member):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
        if not muted_role:
            # Create a muted role if it doesn't exist
            muted_role = await ctx.guild.create_role(name='Muted', reason='Mute')

            # Apply the role to all channels
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        await member.add_roles(muted_role, reason='Mute')
        await ctx.send(f'muted {member}.')
    else:
        await ctx.send('You are not allowed to use this.')

@bot.command(name='purge')
async def purge(ctx, amount: int):
    # Check if the user invoking the command is the allowed user
    if ctx.author.id == allowed_user_id:
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f'Deleted {amount} messages.')
    else:
        await ctx.send('You are not allowed to use this.')

bot.run('MTE5MTExODU3MTkxMzM2NzYwMw.GwZBvX.5z227p_bzk8brHctaykZsShx8xFozBmoguYqYc')
