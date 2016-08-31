import praw
import os
import re

#set globals
r=praw.Reddit('Mod helper by captainmeta4')
ME = r.get_redditor('BotBust')
SUBREDDIT = r.get_subreddit('BotBust')
LOG_SUB = r.get_subreddit('BotBustLog')
LOG_TITLE = "/u/%(user)s banned from /r/%(subreddit)s"

BAN_NOTE = "BotBusted!"
BAN_MESSAGE = "Known comment bots are not welcome in /r/%(subreddit)s!"
WELCOME_MESSAGE = ("Hello, moderators of /r/%(subreddit)s."
                   "\n\nI am now helping keep your subreddit free of known worthless comment bots."
                   "\n\nFor more information, or to submit a worthless bot to my banlist, please visit /r/BotBust."
                   )

class Bot():

    def __init__(self):

        self.friends=[]

    def reload_friends(self):

        self.friends = []

        print('refreshing banlist...')

        for redditor in r.get_friends(limit=None):
            self.friends.append(redditor.name)

        print('...done')

    def login(self):
        
        print('logging in...')
        r.login(ME, os.environ.get('password'))
        print('...done')


    def run(self):

        self.login()
        self.reload_friends()

        while True:
            self.check_for_mod_invites()
            self.check_for_new_banned()
            self.patrol_r_mod()

    def check_for_mod_invites(self):

        print('checking inbox...')

        for message in r.get_unread(limit=None):

            #assume messages are invites

            message.mark_as_read()
            try:
                r.accept_moderator_invite(message.subreddit)
                print('accepted invite to /r/'+message.subreddit.display_name)
                #r.send_message(comment.subreddit, "Reporting for duty!",WELCOME_MESSAGE % {"subreddit":comment.subreddit.display_name}) 
            except:
                pass
        print('...done')

    def patrol_r_mod(self):
        
        #load comments
        print('patrolling /r/mod...')
        for comment in r.get_subreddit('mod').get_comments(limit=200):

            #handle comments by [deleted] users
            if comment.author == None:
                continue

            #ignore removed comments
            if comment.banned_by:
                continue

            #ignore non-friend comments
            if comment.author.name not in self.friends:
                continue

            #ignore comments whose authors are botbustproof
            if "botbustproof" in comment.author_flair_css_class:
                continue

            #at this point the ban needs to be issued
            
            # protect against insufficient mod perms by using try
            try:
                comment.remove()
            except:
                pass

            print('banning /u/'+comment.author.name+' from /r/'+comment.subreddit.display_name)
            try:
                comment.subreddit.add_ban(comment.author, note="BotBusted!", ban_message = BAN_MESSAGE % {"subreddit":comment.subreddit.display_name})
                #self.log_action(comment)
            except:
                pass
        print('...done')

    def log_action(self, comment):

        user = comment.author.name
        sub = comment.subreddit.display_name
        url = comment.permalink

        title = LOG_TITLE % {"user":user, "subreddit":sub}

        r.submit(LOG_SUB, title, url=url)
        
    def check_for_new_banned(self):

        need_to_reload = False

        print('checking for updates to banlist...')

        #process pending bans. search by flair
        for submission in SUBREDDIT.search("flair:to-be-banned",limit=None):

            #ignore any stray search results
            if submission.link_flair_css_class != "to-be-banned":
                continue

            need_to_reload = True

            #get the username
            name = re.match("https?://(\w{1,3}\.)?reddit.com/u(ser)?/([A-Za-z0-9_-]+)/?", submission.url).group(3)

            #friend the redditor
            r.get_redditor(name).friend()
            print(name+" banned!")
            submission.set_flair(flair_text="Banned!", flair_css_class="banned")

            #process pending unbans

        for submission in SUBREDDIT.search("flair:to-be-unbanned"):
            
            if submission.link_flair_css_class != "to-be-unbanned":
                continue

            need_to_reload = True

            #get the username
            name = re.match("https?://(\w{1,3}\.)?reddit.com/u(ser)?/([A-Za-z0-9_-]+)/?", submission.url).group(3)

            #unfriend the redditor
            r.get_redditor(name).unfriend()
            print(name+" unbanned")
            submission.set_flair(flair_text="Unbanned", flair_css_class="unbanned")

        print('...done')
        #reload the banlist
        if need_to_reload:
            self.reload_friends()


        




if __name__=="__main__":
    b=Bot()
    b.run()
