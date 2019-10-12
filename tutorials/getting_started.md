# Getting started

Hello! And welcome to this template for making bots and services with
[Matrix](https://matrix.org). This project is a slightly abstracted layer over
[matrix-nio](https://github.com/poljar/matrix-nio), the low-level library that
actually interfaces with your Matrix homeserver. (If you don't know what Matrix
or a homeserver is, please see [an introduction to Matrix]()).

This getting started page will demonstrate how to use this template to create a
Reminder bot that will remind a user to do something when they request it to.

The bot will have the ability to:

* Remind users of something at a certain time
* List upcoming reminders
* Optionally remind the user via a private message

## Breaking down the problem

Now that we have a goal for our bot, we'll start breaking down the different
pieces needed to build it. One of the easiest ways to do this is envision how
our bot will act from the perspective of a user. A typical interaction for our
Reminder bot might go a little something like this:

1. A user invites us into a room.
2. We accept the invite and join the room.
3. The user creates a new reminder, optionally opting to be reminded by private
   message.
4. We record the reminder and set a timer to go off.
5. When the timer goes off, we send a message either into the room the reminder
   was made in, or directly to the user, depending on what they picked in step
   3.

With this, we have a clear idea of what functionality we'll need to implement
for our bot to do these things.

## Auto-joining a room when invited

Let's start with the first two in this list:

1. A user invites us into a room.
2. We accept the invite and join the room.

Luckily for us nio-template already includes this functionality by default, so
this will already work! Let's look at how this is accomplished as an
introduction.

In `main.py`, an instance of
[nio.AsyncClient](https://matrix-nio.readthedocs.io/en/latest/nio.html#asyncclient)
is created. This client is given an access token provided by the config,
connects to a Matrix server and then proceeds to continuously call the
homeserver's `/sync` endpoint to get new events.

There are many different types of events in Matrix. Messages, typing
notifications, membership events etc. matrix-nio can filter events coming down
the `/sync` stream by type, and run a callback method when that event type is
received.

In `main.py`, nio-template sets up two callback functions. One for
`RoomMessageText` and another for `InviteEvent`. The functions
`callbacks.message` and `callbacks.invite` are then called respectively and
given the events themselves; as well as some metadata such as what room the
event was sent in.

`callbacks.invite` is a function that lives in `callbacks.py`. It receives the
aforementioned room and event objects, then attempts to join the room that the
invite was received from. This is done using the `AsyncClient.join` method.

Great! With this code our bot will auto-accept invites and join any room it's
invited to. Let's move on to the next bits we want the bot to do.

## Creating a reminder

The next two steps were:

3. The user creates a new reminder, optionally opting to be reminded by private
   message.
4. We record the reminder and set a timer to go off.

Step 3 is rather large, so lets unpack it a bit. How will the user create a
reminder? Presumably the user will send a message in a room that the bot is in.
The message should contain a time when the user wants to be reminded, what they
want to be reminded about, and whether it should be via PM or the current room.
How would a message like that look?

Perhaps something like:

```
!reminder room Make cookies for grandma; two days
```

and for the PM usecase:

```
!reminder pm Make cookies for grandma; two days
```

This looks sensible. But before we even worry about what the message looks
like, we need the bot to listen for messages in the first place! Thankfully,
the template already does this by default.

### Listening for messages

Remember how we have a callback on `InviteEvent` which calls `callbacks.invite`
as joins us to a room? Well we also have `RoomMessageText` which calls
`callbacks.message` every time we receive a message!

`callbacks.message` then extracts the text of the message, does some checks to
make sure we aren't processing messages from ourselves, then decides whether
the message is a command or not. A message is a command if it starts with the
configured command prefix, in this instance `!reminder`. If this is the case, a
new `Command` object will be created, which is defined in `bot_commands.py`.

Let's configure our command prefix really quick. If you haven't done so
already, copy the `sample.config.yaml` file to `config.yaml` and open it up.
This is the bot's config file. The default set of options are listed, such as
bot credentials, logging and indeed, the command prefix. Note that all the
options here are extracted by simple code in `config.py`, and defining new
options is easy! Go ahead and change the command prefix to `!reminder`, then
save and quit.

Great! Now when a message reaches the bot starting with `!reminder`, the
message will be interpreted as a command.

### Parsing commands

Open up `bot_commands.py` to the `Command` class. `callbacks.message` creates a
`Command` when it detects a message starting with our command prefix. The
`Command.command` variable will be set to everything after the command prefix,
and `Command.args` will be the same as `Command.command`, but with the first
word removed. For example, if the bot receives the message `!reminder room Wash
the car; 3 hours`, `Command.command` will be `room`, and `Command.args`
will be `Wash the car; 3 hours`.

After creating the `Command` object, `callbacks.message` immediately calls
`Command.process`. The `process()` function checks the contents of
`Command.command`, and calls a handler function based on its contents. There
are a couple default handlers for some common commands, such as `help`, which
users can use to find out more about your bot and what commands can be used.

To add a new command, we simply need to add a new check to `process`. Make two,
one for the `room` command, and one for `pm`. Each `if/elif` statement should
call the corresponding handler function. Since both of these functions both do
similar things, we can just create a single handler function that takes an
argument which decides whether to send the reminder in the room or in a PM.
Create this function, starting with an underscore to indicate that it shouldn't
be accessed outside of the `Command` class. Something like `_make_reminder`.
This function will also need to have a boolean arguement, call it `pm`.

```
class Command(object):
...
    def process(self):
    	...
	elif self.command.startswith("pm"):
	    await self._make_reminder(True)
	elif self.command.startswith("room"):
	    await self._make_reminder(False)
	...
    
    def _make_reminder(self, pm):
        """Create a reminder

	Args:
	    pm (bool): Whether the reminder should be sent in a private message
	        or the room it was sent in.
	"""
        # Make a reminder!
...
```

Remember that `Command.args` will contain something along the lines of `Wash
the car, in two days". Let's start `_make_reminder` off by splitting that into
the two components we want:

```
# Split the command arguments by ";", turning "Eat a hotdog; 12 minutes" into
# "Eat a hotdog" and " 12 minutes"
r_text, r_time = self.args.split(";", 1)
```

The reason we give `1` to `split` is so if the user enters something like
`!reminder room Bake a cake; 15 minutes; something else`, it doesn't cause our
bot to crash (because there's 3 `;`-seperated sections).

Great! We've parsed the command and its arguments. All we need to do now is
schedule our bot is send the text back to the user depending on the value of
`pm`, and we're finished!

## Sending the reminder

* Parse the time
* Figure out whether to send to self.room.room_id or self.event.sender (find or
  start a PM)
* Start a scheduler

## Cleaning things up

* Creating a Reminder class and using that instead
  * Reminder.schedule(human-friendly text)
  * Reminder._send()
  * Reminder.target_room_ids

## Extra Credit

* Loading Reminders to the database and loading them again, persisting across bot restarts
* 'Remind me', 'Remind PM' reactions to also be mentioned

