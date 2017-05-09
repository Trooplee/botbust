import praw
import os
import re
#import cleanup

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

        self.moderated=[]
        self.friends=[]

    def reload_moderated(self):

        self.moderated=[]

        for subreddit in r.get_my_moderation(limit=None):
            self.moderated.append(subreddit.display_name)

    def reload_friends(self):
        self.friends=[]
        for user in r.get_friends(limit=None):
            self.friends.append(user.name)


    def login(self):
        
        print('logging in...')
        r.login(ME, os.environ.get('password'), disable_warning=True)
        print('...done')


    def run(self):

        self.login()
        
        self.check_for_mod_invites()
        self.reload_moderated()
        self.reload_friends()

        while True:
            self.check_for_new_banned()
            self.patrol_r_friends()
            self.check_for_mod_invites()

    def check_for_mod_invites(self):

        print('checking inbox...')

        for message in r.get_unread(limit=None):

            #assume messages are invites

            message.mark_as_read()
            try:
                r.accept_moderator_invite(message.subreddit)
                print('accepted invite to /r/'+message.subreddit.display_name)
                #r.send_message(comment.subreddit, "Reporting for duty!",WELCOME_MESSAGE % {"subreddit":comment.subreddit.display_name}) 
                self.moderated.append(message.subreddit.display_name)
            except:
                pass
        print('...done')

    def patrol_r_friends(self):
        
        #load comments
        print('patrolling /r/friends...')
        for comment in r.get_subreddit('friends').get_comments(limit=100):

            #All comments here will be by a banned account.
            #the only thing to check is that it's in a moderated subreddit

            if comment.subreddit.display_name not in self.moderated:
                continue

            if comment.banned_by:
                continue

            #ignore comments whose authors are botbustproof
            if comment.author_flair_css_class:
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
                self.log_ban(comment)
            except:
                pass
        print('...done')

    def log_ban(self, comment):

        user = comment.author.name
        sub = comment.subreddit.display_name
        url = comment.permalink

        title = LOG_TITLE % {"user":user, "subreddit":sub}

        r.submit(LOG_SUB, title, url=url).approve()
        
    def check_for_new_banned(self):


        print('checking for updates to banlist...')
        need_to_reload=False

        #process pending check-for-bans. search by flair
        for submission in SUBREDDIT.search("flair_css_class:checkban",limit=None):

            #ignore any stray search results
            if submission.link_flair_css_class !="checkban":
                continue

            #get the username
            name = re.match("https?://(\w{1,3}\.)?reddit.com/u(ser)?/([A-Za-z0-9_-]+)/?", submission.url).group(3)

            print('checking ban state on /u/'+name)
            
            if name in self.friends:
                submission.set_flair(flair_text="Already Banned!", flair_css_class="banned")

            else:
                submission.set_flair(flair_text="For Review", flair_css_class = "exclam")
            
            

        #process pending bans. search by flair
        for submission in SUBREDDIT.search("flair_css_class:banpending",limit=None):

            #ignore any stray search results
            if submission.link_flair_css_class != "banpending":
                continue

            need_to_reload = True

            #get the username
            name = re.match("https?://(\w{1,3}\.)?reddit.com/u(ser)?/([A-Za-z0-9_-]+)/?", submission.url).group(3)

            #friend the redditor
            r.get_redditor(name).friend()
            print(name+" banned!")
            submission.set_flair(flair_text="Banned!", flair_css_class="banned")


            #process pending unbans

        for submission in SUBREDDIT.search("flair_css_class:unbanpending"):
            
            if submission.link_flair_css_class != "unbanpending":
                continue

            need_to_reload = True

            #get the username
            name = re.match("https?://(\w{1,3}\.)?reddit.com/u(ser)?/([A-Za-z0-9_-]+)/?", submission.url).group(3)

            #unfriend the redditor
            r.get_redditor(name).unfriend()
            print(name+" unbanned")
            submission.set_flair(flair_text="Unbanned", flair_css_class="unbanned")

        print('...done')

        if need_to_reload:
            self.reload_friends


if __name__=="__main__":
    b=Bot()
    b.run()
