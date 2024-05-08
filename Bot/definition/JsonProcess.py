import os
import json
import aiofiles

class JsonProcess():
    def __init__(self, json_file) -> None:
         self.file = json_file

    async def read_json(self):
        async with aiofiles.open(self.file, mode='r', encoding='utf-8') as file:
            return json.loads(await file.read())
        
    async def write_json(self, data):
        async with aiofiles.open(self.file, mode='w', encoding='utf-8') as file:
            await file.write(json.dumps(data, indent=4, ensure_ascii=False))
        return
    
    @classmethod
    async def format_json(cls, data, args):
        return data.replace('{0}', args)