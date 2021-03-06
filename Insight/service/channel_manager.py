import discord_bot
import random
import discord_bot.channel_types as cType
from functools import partial
import discord
import asyncio
import datetime
import queue
import sys
import traceback
import InsightExc


class Channel_manager(object):
    def __init__(self, service_module):
        self.service = service_module
        self.__channel_feed_container = {}
        self.__dm_container = {}
        self.__discord_client:discord_bot.Discord_Insight_Client = None
        self.__id_locks = {}
        self.__delay_post = queue.Queue()

    async def add_delay(self, other_time):
        zk_module.add_delay(self.__delay_post, other_time)

    async def avg_delay(self):
        result = await self.__discord_client.loop.run_in_executor(None,
                                                                  partial(zk_module.avg_delay, self.__delay_post, True))
        return result

    def feed_count(self):
        return len(self.__channel_feed_container)

    def exists(self, feed_object):
        try:
            assert isinstance(feed_object, cType.insight_feed_service_base)
            return self.__channel_feed_container.get(feed_object.channel_id) == feed_object
        except Exception as ex:
            print(ex)
            return False

    def get_discord_client(self):
        assert isinstance(self.__discord_client,discord_bot.Discord_Insight_Client)
        return self.__discord_client

    def __get_active_channels(self):
        __feeds = list(self.__channel_feed_container.values())
        random.shuffle(__feeds)
        return __feeds

    def sy_get_all_channels(self):
        for channel in self.__get_active_channels():
            yield channel

    async def get_all_channels(self):
        for channel in self.__get_active_channels():
            yield channel

    async def get_all_capRadar(self):
        async for channel in self.get_all_channels():
            if isinstance(channel, cType.insight_capRadar):
                yield channel

    async def get_all_enFeed(self):
        async for channel in self.get_all_channels():
            if isinstance(channel, cType.insight_enFeed):
                yield channel

    async def __get_text_channels(self):
        for guild in self.__discord_client.guilds:
            for channel in guild.text_channels:
                yield channel

    def set_client(self, client_object):
        try:
            assert isinstance(client_object,discord_bot.Discord_Insight_Client)
            self.__discord_client = client_object
        except AssertionError:
            sys.exit(1)

    async def load_channels(self, load_message=True):

        def get_ids():
            db = self.service.get_session()
            try:
                ids = [i.channel_id for i in db.query(tb_channels).all()]
                return ids
            except Exception as ex:
                print(ex)
                return None
            finally:
                db.close()

        if load_message:
            print('Loading feed services... This could take some time depending on the number of feeds.')
        start = datetime.datetime.utcnow()
        existing_ids = await self.__discord_client.loop.run_in_executor(None, get_ids)
        get_channel_tasks = []
        async for i in self.__get_text_channels():
            try:
                if existing_ids is not None:
                    if i.id in existing_ids and self.__channel_feed_container.get(i.id) is None:
                        get_channel_tasks.append(self.get_channel_feed(i))
                else:
                    get_channel_tasks.append(self.get_channel_feed(i))
            except Exception as ex:
                print(ex)
        if len(get_channel_tasks) > 0:
            await asyncio.gather(*get_channel_tasks, return_exceptions=True)
            print("Loaded {} feeds in {:.1f} seconds".format(len(get_channel_tasks),
                                                             (datetime.datetime.utcnow() - start).total_seconds()))

    async def add_feed_object(self,ch_feed_object):
        self.__channel_feed_container[ch_feed_object.channel_id] = ch_feed_object
        await self.refresh_post_all_tasks()
        return ch_feed_object

    async def __add_channel(self,discord_channel_object,ch_feed_object_type):
        return await self.add_feed_object(await ch_feed_object_type.load_new(discord_channel_object,self.service,self.__discord_client))

    async def __remove_container(self,ch_id_int):
        return self.__channel_feed_container.pop(ch_id_int)

    async def __already_exists(self,ch_id):
        try:
            return await self.__discord_client.loop.run_in_executor(None,partial(cType.insight_textChannel_NoFeed.get_existing_feed_type),ch_id,self.service)
        except Exception as ex:
            print(ex)

    async def get_channel_feed(self, channel_object: discord.TextChannel):
        assert channel_object.id is not None
        cLock = self.__id_locks.get(channel_object.id)
        if not isinstance(cLock, asyncio.Lock):
            cLock = asyncio.Lock()
            self.__id_locks[channel_object.id] = cLock
        async with cLock:  # race condition to prevent double loading of channels if timed correctly
            retry_count = 4
            while retry_count > 0:
                try:
                    feed = await self.__get_channel_feed(channel_object)
                    retry_count = 0
                    return feed
                except InsightExc.DiscordError.FeedConvertReload:
                    pass
                except Exception as ex:
                    print('An error occurred when loading a channel feed: {}'.format(ex))
                    traceback.print_exc()
                retry_count -= 1
                await asyncio.sleep(1)
            raise InsightExc.DiscordError.ChannelLoaderError

    async def __get_channel_feed(self,channel_object: discord.TextChannel):
        try:
            assert isinstance(channel_object,discord.TextChannel)
            __feed_obj = self.__channel_feed_container.get(channel_object.id)
            if __feed_obj is not None:
                return __feed_obj
            else:
                __ch_feed_type = await self.__already_exists(channel_object.id)
                if __ch_feed_type is not None:
                    return await self.__add_channel(channel_object,__ch_feed_type)
                else:
                    return cType.insight_textChannel_NoFeed(channel_object, self.service)
        except AssertionError:
            assert isinstance(channel_object,discord.DMChannel)
            return cType.insight_directMessage(channel_object,self.service)

    async def get_user_dm(self, message_object: discord.Message):
        assert isinstance(message_object, discord.Message)
        await message_object.author.send("Opening a new conversation! Hello!")
        dm = message_object.author.dm_channel
        return cType.insight_directMessage(dm, self.service)

    async def delete_feed(self,channel):
        ch_obj = None
        if isinstance(channel,int):
            ch_obj = await self.__remove_container(channel)
        elif isinstance(channel,discord.TextChannel):
            ch_obj = await self.__remove_container(channel.id)
        if ch_obj is not None:
            if await ch_obj.delete():
                return True
            else:
                return False

    def post_message(self,message_txt):
        for feed in self.sy_get_all_channels():
            try:
                feed.add_message(message_txt)
            except Exception as ex:
                print(ex)

    def send_km(self, km):
        assert isinstance(km, tb_kills)
        for feed in self.sy_get_all_channels():
            try:
                feed.add_km(km)
            except Exception as ex:
                print(ex)

    async def refresh_post_all_tasks(self):
        try:
            async for feed in self.get_all_channels():
                try:
                    if feed.deque_done():
                        feed.set_deque_task(self.__discord_client.loop.create_task(feed.post_all()))
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)

    async def auto_refresh(self):
        while True:
            await self.refresh_post_all_tasks()
            await asyncio.sleep(60)

    async def auto_channel_refresh(self):
        while True:
            await self.load_channels(load_message=False)
            await asyncio.sleep(3600)


from database.db_tables.eve import tb_kills
from database.db_tables.discord import tb_channels
from service.zk import zk as zk_module
