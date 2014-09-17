'''
'Reddit Imgdownloader original work from http://inventwithpython.com/blog/2013/09/30/downloading-imgur-posts-linked-from-reddit-with-python/
'''
import re, praw, requests, os, glob, sys, mmap
from bs4 import BeautifulSoup

MIN_SCORE = 100 # the default minimum score before it is downloaded
FOLD = "Data"
DNUM = 100



if len(sys.argv) < 2:
    # no command line options sent:
    print('Usage:')
    print('  python %s subreddit FOLDER NUM [minimum score]' % (sys.argv[0]))
    sys.exit()
elif len(sys.argv) >= 2:
    # the subreddit was specified:
    targetSubreddit = sys.argv[1]
    if len(sys.argv) >= 3:
        # the desired minimum score was also specified:
        FOLD = str(sys.argv[2])
        DNUM = int(sys.argv[3])
        MIN_SCORE = int(sys.argv[4])
try:
    f = open(FOLD + "/" + targetSubreddit + ".done")
    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
except:
    urllog = open(FOLD + "/" + targetSubreddit + ".done", "a")
    urllog.close()	
	
imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
try:
    os.makedirs(FOLD)
except:
    pass
def downloadImage(imageUrl, localFileName):
    try:
        if s.find(localFileName) != -1:
            print 'File Exist, Skipping...'
            return
    except:
	    print "!",
    pass
  
    fName, fExt = os.path.splitext(localFileName)
    global SSTART
    try:
        ofile = open(FOLD + "/" + targetSubreddit + ".cache", "r")
        NSTART = ofile.read()
        NSTART = int(NSTART)
    except:
        NSTART = 1	
    
    urllog = open(FOLD + "/" + targetSubreddit + ".done", "a")

    saveName = targetSubreddit + "_" + str(NSTART) + fExt
    log = open(FOLD + "/" + targetSubreddit + ".cache", "w")

    response = requests.get(imageUrl)
    if response.status_code == 200:
        print('Downloading %s' % (localFileName))
        try:
            with open(FOLD+"/"+ saveName, 'wb') as fo:
                NSTART += 1
                for chunk in response.iter_content(4096):
                    fo.write(chunk)
            log.write(str(NSTART))
            urllog.write(localFileName + "\n")
        except:
            print "Error :", sys.exc_info()[0]
        pass			
    log.close()
    urllog.close()
# Connect to reddit and download the subreddit front page
r = praw.Reddit(user_agent='CHANGE THIS TO A UNIQUE VALUE') # Note: Be sure to change the user-agent to something unique.
submissions = r.get_subreddit(targetSubreddit).get_hot(limit=DNUM)
# Or use one of these functions:
#                                       .get_top_from_year(limit=25)
#                                       .get_top_from_month(limit=25)
#                                       .get_top_from_week(limit=25)
#                                       .get_top_from_day(limit=25)
#                                       .get_top_from_hour(limit=25)
#                                       .get_top_from_all(limit=25)

# Process all the submissions from the front page


for submission in submissions:
    # Check for all the cases where we will skip a submission:
    if "imgur.com/" not in submission.url:
        continue # skip non-imgur submissions
    if submission.score < MIN_SCORE:
        continue # skip submissions that haven't even reached 100 (thought this should be rare if we're collecting the "hot" submission)
    if len(glob.glob('reddit_%s_%s_*' % (targetSubreddit, submission.id))) > 0:
        continue # we've already downloaded files for this reddit submission

    if 'http://imgur.com/a/' in submission.url:
        # This is an album submission.
        albumId = submission.url[len('http://imgur.com/a/'):]
        htmlSource = requests.get(submission.url).text

        soup = BeautifulSoup(htmlSource)
        matches = soup.select('.album-view-image-link a')
        for match in matches:
            imageUrl = match['href']
            if '?' in imageUrl:
                imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
            else:
                imageFile = imageUrl[imageUrl.rfind('/') + 1:]
            localFileName = 'reddit_%s_%s_album_%s_imgur_%s' % (targetSubreddit, submission.id, albumId, imageFile)
            
            if DNUM == 0:
                print("Done")
                sys.exit()	
            print(str(DNUM) + ":"),
            downloadImage('http:' + match['href'], localFileName)
            DNUM -= 1

    elif 'http://i.imgur.com/' in submission.url:
        # The URL is a direct link to the image.
        mo = imgurUrlPattern.search(submission.url) # using regex here instead of BeautifulSoup because we are pasing a url, not html

        imgurFilename = mo.group(2)
        if '?' in imgurFilename:
            # The regex doesn't catch a "?" at the end of the filename, so we remove it here.
            imgurFilename = imgurFilename[:imgurFilename.find('?')]

        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, imgurFilename)
       
        if DNUM == 0:
            print("Done")
            sys.exit()	
        print(str(DNUM) + ":"),
        downloadImage(submission.url, localFileName)
        DNUM -= 1

    elif 'http://imgur.com/' in submission.url:
        # This is an Imgur page with a single image.
        htmlSource = requests.get(submission.url).text # download the image's page
        soup = BeautifulSoup(htmlSource)
        imageUrl = soup.select('.image a')[0]['href']
        if imageUrl.startswith('//'):
            # if no schema is supplied in the url, prepend 'http:' to it
            imageUrl = 'http:' + imageUrl
        imageId = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('.')]

        if '?' in imageUrl:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:imageUrl.rfind('?')]
        else:
            imageFile = imageUrl[imageUrl.rfind('/') + 1:]

        localFileName = 'reddit_%s_%s_album_None_imgur_%s' % (targetSubreddit, submission.id, imageFile)
        
        if DNUM == 0:
            print("Done")
            sys.exit()	
        print(str(DNUM) + ":"),
        downloadImage(imageUrl, localFileName)
        DNUM -= 1