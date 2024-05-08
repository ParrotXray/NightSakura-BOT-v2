import os
import json 
import aiofiles

class Language():
    def __init__(self) -> None:
        self.language_file_path = os.path.join("database", "language.json")
        self.en_file_path = os.path.join("language", "content", "en.json")
        self.jp_file_path = os.path.join("language", "content", "jp.json")
        self.tw_file_path = os.path.join("language", "content", "tw.json")
        self.cn_file_path = os.path.join("language", "content", "cn.json")
    
    async def json_process_read(self, json_file):
        async with aiofiles.open(json_file, mode='r', encoding='utf-8') as file:
            return json.loads(await file.read())
    
    async def json_process_write(self, json_file, data):
        async with aiofiles.open(json_file, mode='w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))
        return
        
    async def language_process(self, guild_id):
        data = await self.json_process_read(self.language_file_path)
        if str(guild_id) in data:
            option_language = {
                "US": self.en_file_path,
                "JP": self.jp_file_path,
                "TW": self.tw_file_path,
                "CN": self.cn_file_path
            }
            return await self.json_process_read(option_language.get(data[str(guild_id)]))
        else:
            data[str(guild_id)] = "US"
            await self.json_process_write(self.language_file_path, data)
            option_language = {
                "US": self.en_file_path,
                "JP": self.jp_file_path,
                "TW": self.tw_file_path,
                "CN": self.cn_file_path
            }
            return await self.json_process_read(option_language.get(data[str(guild_id)]))

    async def language_core_msg(self, guild_id):
        core_language = await self.language_process(guild_id)
        return core_language['core']
    
    async def language_delay_msg(self, guild_id):
        delay_language = await self.language_process(guild_id)
        return delay_language.get('delay')
    
    async def language_support_msg(self, guild_id):
        support_language = await self.language_process(guild_id)
        return support_language.get('support')
    
    async def language_info_msg(self, guild_id):
        info_language = await self.language_process(guild_id)
        return info_language.get('info')
    
    async def language_subscription_msg(self, guild_id):
        subscription_language = await self.language_process(guild_id)
        return subscription_language.get('subscription')
    
    async def language_update_msg(self, guild_id):
        update_language = await self.language_process(guild_id)
        return update_language.get('update')
    
    async def language_userinfo_msg(self, guild_id):
        userinfo_language = await self.language_process(guild_id)
        return userinfo_language.get('userinfo')
    
    async def language_serverinfo_msg(self, guild_id):
        serverinfo_language = await self.language_process(guild_id)
        return serverinfo_language.get('serverinfo')
    
    async def language_autorole_msg(self, guild_id):
        autorole_language = await self.language_process(guild_id)
        return autorole_language.get('autorole')

    async def language_reactionrole_msg(self, guild_id):
        reactionrole_language = await self.language_process(guild_id)
        return reactionrole_language.get('reactionrole')

    async def language_member_msg(self, guild_id):
        member_language = await self.language_process(guild_id)
        return member_language.get('member')
    
    async def language_music_msg(self, guild_id):
        music_language = await self.language_process(guild_id)
        return music_language.get('music')
    

class CommandLanguage():
    def __init__(self) -> None:
        self.jp_file_path = os.path.join("language", "command", "jp.json")
        self.tw_file_path = os.path.join("language", "command", "tw.json")
        self.cn_file_path = os.path.join("language", "command", "cn.json")

    def json_process_read(self, json_file):
        with open(json_file, "r" ,encoding="utf8") as file:  
            return json.load(file)

    def command_tw_msg(self):
        return self.json_process_read(self.tw_file_path)
    
    def command_jp_msg(self):                      
        return self.json_process_read(self.jp_file_path)
    
    def command_cn_msg(self):
        return self.json_process_read(self.cn_file_path)