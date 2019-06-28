from discord.ext.commands import Context

from bot.bot import MusicBot
from bot.cogs.music_settings import MusicSettingsCog
from dsp.audio_object import AudioSequence


def process_audio(bot: MusicBot, ctx: Context, audio: AudioSequence) -> AudioSequence:
    cog: MusicSettingsCog = bot.get_cog('MusicSettingsCog')
    ct = cog.contexts[ctx.guild.id]
    for name, ext in ct.items():
        print(ext)
        if ext.enabled:
            audio = ext.process(audio)
    return audio
