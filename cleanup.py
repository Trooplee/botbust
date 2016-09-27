import praw

r=praw.Reddit('Cleanup script for botbust by /u/captainmeta4')

r.login('BotBust',input('password for botbust: '), disable_warning=True)

#define a generator that takes a username and returns the corresponding posts on /r/botbust
def get_posts(name):

    for submission in r.search("title:"+name, subreddit="botbust"):
        if name not in submission.title:
            continue
        yield submission

#load ban list

friends=[]
for user in r.get_friends(limit=None):
    print("checking /u/"+user.name)

    #try loading the user
    try:
        user.refresh()
    except praw.errors.NotFound:
        #user is shadowbanned
        print(user.name+" is shadowbanned")
        user.unfriend()
        for submission in get_posts(user.name):
            print(submission.title)
            submission.set_flair(flair_text="Shadowbanned", flair_css_class="x")

    if vars(user).get('is_suspended', False):
        print(user.name+" is suspended")
        user.unfriend()
        for submission in get_posts(user.name):
            print(submission.title)
            submission.set_flair(flair_text="Suspended", flair_css_class="x")

    print("")

print('done')
