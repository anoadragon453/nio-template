#!/usr/bin/env python3

import asyncio
from matrixbot.bot import Bot


bot = Bot("config.yaml")
asyncio.get_event_loop().run_until_complete(bot.login())
