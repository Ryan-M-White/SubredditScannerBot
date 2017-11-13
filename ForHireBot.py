import praw
import time

credsFile = open("creds.txt", "r")
creds = [x.strip('\n\r') for x in credsFile.readlines()]
reddit = praw.Reddit(client_id=str(creds[0]), client_secret=str(creds[1]), password=str(creds[2]), user_agent =str(creds[3]), username=str(creds[4])) #Login
print("Logging in...")
print(reddit.user.me())
words_to_match = ["[Hiring]", "[HIRING]", "[hiring]"]
cacheFile = open("cache.txt", "r+")
cache = [x.strip('\n\r') for x in cacheFile.readlines()]


def run_bot():
    print("Grabbing subreddit...")
    target = "forhire"
    results = reddit.subreddit(target).new(limit=50) #Pull posts from subreddit.
    print("Grabbing posts from /r/" + target)
    print("")
    for submission in results:
        title_text = submission.title
        isMatch = any(string in title_text for string in words_to_match)
        if submission.id not in cache and isMatch: 
            #Found a new hiring post, print contents.
            print("Match found!") 
            print("    Submission ID: " + submission.id)
            print("    Submisison Title: " + submission.title)

            #Construct a message with the contents of the post and any other useful info
            urlFriendlyTitle = title_text.replace("+", "%2B") #Replace any + signs with their utf-8 equivalent            
            urlFriendlyTitle = urlFriendlyTitle.replace(" ", "+") #Replace any spaces with + signs, so the template subject line has spaces if needed
            messageBody = "**Post Title:** " + title_text + "\n\n" + "**Post Description:**\n\n" + submission.selftext + "\n\n**Go to Post:** " + submission.url + "\n\n**Response Template:** https://www.reddit.com/message/compose?to=" + str(submission.author) + "&subject=re:+" + urlFriendlyTitle + "&message="
            #Send me the message (Was going to try and make the bot send me an email, but realized it's much simpler to just let reddit do the leg work. Since I use reddit mobile, I'll get a push notification anyway.)
            reddit.redditor(creds[4]).message("New hiring post in /r/ForHire", messageBody)
            print("    Notification sent")
            print("")


            #Cache the submission so the bot knows it's seen the post. Don't spam my inbox.
            cache.append(submission.id)
            cacheFile.write(str(submission.id) + "\n\r")
    print("Submissions loop finished, time to sleep.")
    cacheFile.close()
    #print("Cache: ")   
    #print(cache)


while True:
    run_bot()
    time.sleep(1800) #Run this script ever half hour.





#Reminder: Once bot finds a home, remember to disable print statements
