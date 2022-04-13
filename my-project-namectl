#!/usr/bin/env python3
import asyncio

try:
    from my_project_name import main

    # Run the main function of the bot
    asyncio.get_event_loop().run_until_complete(main.main())
except ImportError as e:
    print("Unable to import my_project_name.main:", e)
