# BotBust

BotBust is a moderation assistance bot that bans known crappy comment bots. [Click here to view full details on /r/BotBust](https://redd.it/5092dg)

# Running your own copy

If you moderate multiple networked subreddits, you may wish to use a clone of this bot to maintain a banlist across your network.

To run your own copy of this bot:

1. Fork this repository
2. Create a new reddit account (to run the bot on) and two new subreddits (One to have the ban list, the other to serve as the logging subreddit)
3. Change the user agent string on line 7 to something that doesn't include my name. (Remember, per reddit API rules, you *must* be honest with your user agent string.)
4. Change the global variables in lines 7-13 of botbust.py as needed
5. Make sure that `r=praw.Reddit('section')` uses a valid section of your praw.ini file.
