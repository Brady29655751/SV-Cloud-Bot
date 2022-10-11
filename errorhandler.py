import os
import discord
import datetime as dt
import utility as utils
import filehandler as fh

class Error:
    def __init__(self, error_msg, channel_id, content):
        self.time = (dt.datetime.now() + dt.timedelta(hours=8)).strftime('%Y/%m/%d %H:%M:%S')
        self.error = error_msg
        self.channel_id = channel_id
        self.content = content
        self.error_dict = {
            '時間': self.time,
            '錯誤': self.error,
            '頻道': self.channel_id,
            '內容': self.content
        }
        self.prompt = utils.dict_to_str_list(self.error_dict, True)
    
    def __repr__(self):
        return self.prompt

def get_error(error_msg, channel_id=-1, content="System Error"):
    error = Error(error_msg, channel_id, content)
    path = os.path.join('.', 'error_report.txt')
    fh.write(path, error.prompt)
    return error

async def error_report(content, channel, error_msg):
    error = get_error(error_msg, channel.id, content)
    try:
        await channel.send(f'資工雲割了，請等待重啟（約5分鐘）。\n' + error)
    except Exception:
        # If unable to send msg to discord, restart the bot.
        # Otherwise, it's a normal error and no need to restart.
        os.system("kill 1")
    