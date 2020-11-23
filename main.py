import pickle

import discord
from discord.ext import commands

from config import settings

__ver__ = '1.5.2'

HELP_TXT = '''\
-- Incognito bot - bot for private chatting --
Commands:
> `>h` or `>help`
> Show this help

> `>sup` or `>support`
> Link to support - server
 
> `>c` or `>chats`
> Show your chats
 
> `>v` or `>version`
> Show bot version

> `>s` `[chat]` `[message]`
> send `message` to `chat`

> `>j` `[chat name]` `*[password]` `[name]`
> Join to `chat` with name `name`, area `password` can be followed

> `>n` `[name]` `*[password or is public]`
> Create new room with name `name`. If area `password or is public`
> is followed, chat will be without password and not public...
> Elso if area `password or is public` is number it will be public
>  If area is symbolic it will be a password
> WARRING: Name and password can be with spaces (" ")!

||If you founded any mistakes, please say us!||

'''

class Room ():
    def __init__ (self, name, password = False, is_public = False):
        self._name = name.capitalize ()
        self._pasw = password
        self._is_public = is_public

        self._mems = [] # mems ID
        self._mems_names = []

    def __repr__ (self):
        return f'<room \'{self._name}\', pasw \'{self._pasw}\'>'

    def add_memb (self, memb_id, memb_name):
        if self.is_in (memb_name.capitalize ()) or self.is_in (memb_id):
            return False
        
        self._mems.append (memb_id)
        self._mems_names.append (memb_name.capitalize ())

        return self._mems.copy (), self._mems_names.copy ()

    def find_memb (self, memb_id_or_name):
        if type (memb_id_or_name) == str:
            for i, memb in enumerate (self._mems_names):
                if memb == memb_id_or_name.capitalize ():
                    return i
                
            return False

        else:
            for i, memb in enumerate (self._mems):
                if memb == memb_id_or_name:
                    return i

            return False

    def remove_memb (self, memb_pos):
        if memb_pos:
            self._mems.pop (memb_pos)
            self._mems_names.pop (memb_pos)

            return self._mems.copy (), self._mems_names.copy ()

        return False

    def get_id_and_name (self, memb_pos):
        if type (memb_pos) != bool:
            memb_id = self._mems [memb_pos]
            memb_name = self._mems_names [memb_pos]

            return memb_id, memb_name

        return False
        
    def is_in (self, memb_id_or_name):
        if type (memb_id_or_name) == str:
            return memb_id_or_name.capitalize () in self._mems_names

        return memb_id_or_name in self._mems
        
    def rename_memb (self, memb_pos, new_name):
        if memb_pos:
            prev_mems_names = self._mems_names.copy ()
            
            self._mems_names [memb_pos] = new_name.capitalize ()

            return self._mems, prev_mems_names, prev_mems_names [memb_pos]

        return False

    def is_public (self):
        return self._is_public

    def get_password (self):
        return self._pasw

    def get_mems (self):
        return self._mems.copy ()

    def get_name (self):
        return self._name


if __name__ == '__main__': ##################################
    def read_data ():
        with open (settings ['file'], 'rb') as file:
            data = pickle.load (file)

        return data

    def write_data (data):
        with open (settings ['file'], 'wb') as file:
            pickle.dump (data, file)

    def in_DB (memb_id):
        data = read_data ()

        if not (memb_id in data [1]):
            data [1] [memb_id] = []

        write_data (data)

    async def send_all (mems, message):
        for memb in mems:
            await bot.get_user (memb).send (message)

    async def new_room (message):
        data = read_data ()

        memb_id = message.author.id

        content = message.content.split (' ')
        content_len = len (content)

        if content_len == 0 or content_len == 1:
            return False

        elif content_len == 2:
            room = Room (content [1])

        elif content_len >= 3:
            if content [2].isdigit ():
                room = Room (content [1], is_public = True)

            else:
                room = Room (content [1], content [2].capitalize ())

        if room.get_name () in [chat.get_name () for chat in data [0]]:
            await message.author.send ('Choose anower name for room')
            return False

        contact_data = room.add_memb (memb_id, 'Owner')

        await send_all (contact_data [0], f'{room.get_name ()}: Room created!')
        
        data [1] [memb_id].append (room)
        data [0].append (room)

        write_data (data)

    async def send_command (message):
        data = read_data () [1]
        
        content = message.content.split (' ')
        content_len = len (content)

        if content_len == 2:
            await message.author.send ('Cannot send empty message')
            return False

        elif content_len >= 3:
            for chat in data [message.author.id]:
                if chat.get_name () == content [1].capitalize ():
                    room = chat
                    break
            
            else:
                await message.author.send ('You cannot send messages to this chat')
                return False

            sender_name = room.get_id_and_name (room.find_memb (message.author.id)) [1]

            await send_all (room.get_mems (), f'{sender_name} in chat {room.get_name ()}: {" ".join (content [2:])}')

    async def go_room (message):
        data = read_data ()
        
        memb_id = message.author.id

        content = message.content.split (' ')
        content_len = len (content)

        if content_len <= 2:
            await message.author.send ('O_o Entry to what?')
            return False

        elif content_len == 3:        
            room_to_find = content [1].capitalize ()

            for chat in data [0]:
                if (chat.get_name () == room_to_find) and not chat.get_password ():
                    room = chat

                    break

            else:
                await message.author.send ('Room not found ¯\\\_(ツ)\_/¯')
                return False

            if room.is_in (content [2].capitalize ()):
                message.author.send ('Choose anower name. ¯\\\_(ツ)\_/¯')

                return False

            room.add_memb (memb_id, content [2].capitalize ())

            await send_all (room.get_mems (), f'{room.get_name ()}: {content [2].capitalize ()} joined!')

            data [1] [memb_id].append (room)

        elif content_len == 4:
            room_to_find = content [1].capitalize ()

            for chat in data [0]:
                if (chat.get_name () == room_to_find) and (chat.get_password () == content [2]):
                    room = chat

                    break

            else:
                await message.author.send ('Room not founded ¯\\\_(ツ)\_/¯')
                return False

            if room.is_in (content [2].capitalize ()):
                message.author.send ('Choose anower name. ¯\\\_(ツ)\_/¯')

                return False

            room.add_memb (memb_id, content [3].capitalize ())

            await send_all (room.get_mems (), f'{room.get_name ()}: {content [3].capitalize ()} joined!')

            data [1] [memb_id].append (room)

        write_data (data)

    async def my_rooms (user):
        rooms = read_data () [1] [user.id]

        if rooms:
            for i, room in enumerate (rooms):
                await user.send (f'{i + 1}. {room.get_name ()} {room.get_password () if room.get_password () else ""}')

        else:
            await user.send (':( You didn\'t join any room yet... If you don\t now how to join a room type ">help"')

    async def rename (message):
        content = message.content.split (' ')
        content_len = len (content)

        data = read_data () 

        if content_len == 1:
            await message.author.send ('o_O rename where how? i don\'t now!')

        elif content_len == 2:
            await message.author.send ('o_O rename to who?')

        elif content_len >= 3:
            for chat in data [1] [message.author.id]:
                if chat.get_name () == content [1].capitalize ():
                    room = chat
                    break
            
            else:
                await message.author.send ('You don\'t in this chat')
                return False

            if room.is_in (content [2].capitalize ()):
                message.author.send ('Choose anower name. ¯\\\_(ツ)\_/¯')

                return False

            room.rename_memb (room.find_memb (message.author.id), content [2].capitalize ())

            write_data (data)

    async def exit_room (message):
        content = message.content.split (' ')

    #'''
    bot = commands.Bot (command_prefix = settings ['prefix'])

    @bot.event
    async def on_ready ():
        print (f'Cur ver {__ver__}')

        activity = discord.Activity (name = 'за тобой', type = discord.ActivityType.watching)
        await bot.change_presence (activity = activity)
        
    @bot.event
    async def on_message (message):
        if message.author == bot.user:
            return None

        in_DB (message.author.id)

        if message.content.startswith ('h'):
            await message.author.send ('To get help for bot type\n> >help')
        
        if message.content.startswith ('>'):
            if message.content.startswith ('>n'):
                await new_room (message)

            elif message.content.startswith ('>sup'):
                await message.channel.send (f'Link to support server: {settings ["server"]}')

            elif message.content.startswith ('>s'):
                await send_command (message)

            elif message.content.startswith ('>j'):
                await go_room (message)

            elif message.content.startswith ('>h'):
                await message.channel.send (HELP_TXT)

            elif message.content.startswith ('>c'):
                await my_rooms (message.author)

            elif message.content.startswith ('>v'):
                await message.channel.send (f'Version: {__ver__}')

            elif message.content.startswith ('>r'):
                await rename (message)

            else:
                await message.channel.send ('Sorry, i don\'t know this command, type `>help` to get more info...')

    bot.run (settings ['token'])
    #''' # RED
