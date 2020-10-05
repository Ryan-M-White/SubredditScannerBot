#python package declarations
import praw
import time
from datetime import datetime
import pytz

#Information for the subreddit we want to search
target = "forhire" #Your desired Subreddit.
target_Post_Type = "hiring" 
words_To_Match = ["[hiring]"] #Keywords we want to target and be notified about.
words_Not_To_Match = ["logo", "illustrator", "student blogger", "journalist"] #Keywords to filter out.
post_Grab_Limit = 20 #Adjust based on your target's frequency of new posts.
                     #Reddit returns a maximum of 100 posts per request.


#login and print user info to verify
creds_File = open("creds.txt", "r")
creds = [x.strip('\n') for x in creds_File.readlines()]
reddit = praw.Reddit(client_id = str(creds[0]), 
                    client_secret = str(creds[1]), 
                    password = str(creds[2]),
                    user_agent = str(creds[3]),
                    username = str(creds[4]))
print("Logging in...")
logged_In_User = str(reddit.user.me())
print("Successfully logged in as: " + logged_In_User)
print("")



# This is our actual script that will do all of the work
def run_bot():

    #Create array of cached posts, so we don't re-notify user of old posts.
    cache_File = open("cache.txt", "r+")
    cache = [x.strip('\n') for x in cache_File.readlines()]

    #Let's dig!
    print("Begin loop...")
    print("Grabbing posts from the subreddit /r/" + target + "...")
    results = reddit.subreddit(target).new(limit=post_Grab_Limit) #Pull X number of posts from {{target}} subreddit.
    matchesFound = 0
    print("")

    for submission in results:
        parseable_Title = submission.title.lower() #All lowercase makes parsing easier

        #IGNORE UNWANTED SUBMISSIONS
        is_Not_Match = any(string in parseable_Title for string in words_Not_To_Match)
        if submission.id not in cache and is_Not_Match:
            #Cache the submission so the bot knows it's already checked this one. 
            cache.append(submission.id)
            cache_File.write(str(submission.id) + "\n")

        #MATCHING SUBMISSION FOUND!
        is_Match = any(string in parseable_Title for string in words_To_Match)
        if submission.id not in cache and is_Match: 
            #Found a new hiring post, print contents.
            print("Match found!") 
            print("    Submission ID: " + submission.id)
            print("    Submisison Title: " + submission.title)

            #Construct a message with the contents of the post and any other useful info.
            urlFriendlyTitle = submission.title.replace(" ", "%20") #Encode all spaces that were in the post title.
            message_Body = "**Post Title:** " + submission.title 
            message_Body += "\n\n" + "**Post Description:**\n\n" + submission.selftext 
            message_Body += "\n\n**Go to Post:** " + submission.url 
            message_Body += "\n\n**Response Template:** https://old.reddit.com/message/compose?to=" + str(submission.author) + "&subject=re:%20" + urlFriendlyTitle + "&message="

            #Send the user the message (Will send to your inbox by default, change recipient to a string of the username you want if desired).
            recipient = creds[4]
            reddit.redditor(recipient).message("New " + target_Post_Type + " post in /r/" + target, message_Body) #message(Subject,body)
            print("    Notification sent")
            print("")

            #Cache the submission so the bot knows it's seen the post. Don't spam user's inbox with repeat data.
            cache.append(submission.id)
            cache_File.write(str(submission.id) + "\n")
            matchesFound += 1

    #Loop is done. Print sleep message.
    print("")        
    print("Matches found: " + str(matchesFound))
    print("Loop finished. Time to sleep.")

    #Display time of most recent loop.
    tz_NY = pytz.timezone('America/New_York') 
    datetime_NY = datetime.now(tz_NY)
    print("Last loop occurred:", datetime_NY.strftime("%a %b %d, %I:%M:%S%p")) #day month numDayOfMonth, 1-12HR:Mins:Secs:AM/PM
    print("")
    #Clear cache array and close cache file.
    cache = []
    cache_File.close()


#Some simple demonstration functions for what a bot account can do
def create_Reddit_Post(subreddit, type, title, post_Body):
    if type == "text":
        reddit.subreddit(subreddit).submit(title=title,selftext=post_Body)
        print("created a text post on r/" + subreddit)

    if type == "link":
        reddit.subreddit(subreddit).submit(title,url=post_Body)
        print("created a link post on r/" + subreddit)

def respond_To_A_Post(target_Post,comment):
    submission = reddit.submission(url=target_Post)
    submission.reply(comment)

def get_Mods(subreddit):
    for mods in reddit.subreddit(subreddit).moderator():
        print(mods)


#Activate Bot Functionality
#print("Welcome to Ryan White's Python Reddit API Wrapper Bot Tutorial")

#Create a post.
#create_Reddit_Post("test","text","Learning to make bots is so cool!!!","This is a test post for a presentation I'm doing")
#create_Reddit_Post("RIT","link","Doing presentations is fun","www.rit.edu")

# #Comment on a known submission.
#respond_To_A_Post("https://old.reddit.com/r/test/comments/j5f1ua/","We'll figure it out together!")

# #Print out a list of Moderators for a subreddit
#get_Mods("RIT")

#infinite loop so the bot stays running
while True:
    run_bot()
    time.sleep(1800) #Run this script every half hour.
