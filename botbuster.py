import praw
import os
import re

#set globals
r=praw.Reddit('Mod helper by captainmeta4')
ME = r.get_redditor('BotBust')
SUBREDDIT = r.get_subreddit('BotBust')

BAN_NOTE = "BotBusted!"
BAN_MESSAGE = "Known comment bots are not welcome in /r/%(subreddit)s!"

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

        while True:
            self.check_for_mod_invites()
            self.check_for_new_banned()
            self.patrol_r_mod()

    def check_for_mod_invites(self):

        print('checking inbox...')

        for message in r.get_inbox(limit=None):

            #assume messages are invites

            message.mark_as_read()
            try:
                r.accept_moderator_invite(message.subreddit)
                print('accepted invite to /r/'+message.subreddit.display_name)
            except:
                pass
        print('...done')

    def patrol_r_mod(self):
        
        #load comments
        print('patrolling /r/mod...')
        for comment in r.get_subreddit('mod').get_comments(limit=100):

            #handle comments by [deleted] users
            if comment.author == None:
                continue

            #ignore non-friend comments
            if comment.author.name not in self.friends:
                continue

            #at this point the ban needs to be issued
            comment.remove()
            print('banning /u/'+comment.author.name+' from /r/'+comment.subreddit.display_name)
            comment.subreddit.add_ban(comment.author, note="BotBusted!", ban_message = BAN_MESSAGE % {"subreddit":comment.subreddit.display_name})
        print('...done')
        
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
            name = re.match("https?://reddit.com/u(ser)?/(\w+)/?", submission.url).group(2)

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
            name = re.match("https?://reddit.com/u(ser)?/(\w+)/?", submission.url).group(2)

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
