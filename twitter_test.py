import os
import re
import sys
import json
import time
import random
import datetime

import cv2
import twitter
import numpy as np
import wikipedia as wik


def write_on_img(img, outname, text="FUCK", loc=(200,200),
                 font=cv2.FONT_HERSHEY_PLAIN, size=3,
                 color=(255, 255, 255), thickness=1):
  '''This function writes text onto an image and then writes 
     the resulting image to disk.'''
  img = cv2.putText(img, text, loc, font, size, (0,0,0), thickness+8)
  img = cv2.putText(img, text, loc, font, size, (255,255,255), thickness+5)
  img = cv2.putText(img, text, loc, font, size, color, thickness)
  #cv2.imwrite(outname, img)
  return img

def write_randomly(img, outname, text):
  '''This function writes text onto an image with random colors, 
     a random location and with random size and thickness.'''
  x = random.randint(0, img.shape[1] - img.shape[1] // 4)
  y = random.randint(0, img.shape[0] - img.shape[0] // 4)
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)
  size = random.randint(1, 10)
  thickness = random.randint(3, 10)
  write_on_img(img, outname, text=text, loc=(x, y), size=size, color=(r, g, b))

def write_meme(img, outname, textupp, textlow, maxlinelen=6, imdiv=12):
  line1up = " ".join(textupp[:maxlinelen])
  line2up = " ".join(textupp[maxlinelen:2*maxlinelen])
  line1lo = " ".join(textlow[:maxlinelen])
  line2lo = " ".join(textlow[maxlinelen:2*maxlinelen])
  r = random.randint(0, 255)
  g = random.randint(0, 255)
  b = random.randint(0, 255)
  img = write_on_img(img, outname, text=line1up, loc=(0, img.shape[0] // imdiv), size=4, color=(r, g, b), thickness=5)
  img = write_on_img(img, outname, text=line2up, loc=(0, 2 * img.shape[0] // imdiv), size=4, color=(r, g, b), thickness=5)
  img = write_on_img(img, outname, text=line2lo, loc=(0, img.shape[0] - img.shape[0] // imdiv), size=4, color=(r, g, b), thickness=5)
  img = write_on_img(img, outname, text=line1lo, loc=(0, img.shape[0] - (2 * img.shape[0] // imdiv)), size=4, color=(r, g, b), thickness=5)
  return img

def read_txt(txtfilename):
  '''Reads in a text file and returns it as a list of 
     strings that are space separted words.'''
  with open(txtfilename, "r") as txtfile:
    line = " ".join(txtfile.readlines())
    return line.split()

def return_random_text(textList, minstrlen=3, maxstrlen=12):
  '''Given a list of strings, this returns a random sublist 
     of the text.'''
  randomlen = random.randint(minstrlen, maxstrlen)
  r = random.randint(0, len(textList) - randomlen - 1)
  randstringlist = textList[r : r + randomlen]
  return randstringlist

def choose_random_file(direct):
  files = os.listdir(direct)
  return files[random.randint(0, len(files) - 1)]

def create_dumb_memes(txtDir, imgDir, outDir):
    intxt =  os.path.join(txtDir, choose_random_file(txtDir))
    img = choose_random_file(imgDir)
    inimg = os.path.join(imgDir, img)
    outimg = os.path.join(outDir, img)
    text = read_txt(intxt)
    meme = write_meme(cv2.imread(inimg), outimg, return_random_text(text), return_random_text(text))
    
    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('MeMe_%Y-%m-%d__%H:%M:%S')
    cv2.imwrite(os.path.join(outDir, timestamp + ".jpg"), meme)
    

def create_alg_arts(inDir):
    inFiles = [os.path.join(inDir, f) for f in os.listdir(inDir) if (f.endswith('.jpg') or f.endswith('.jpeg'))]
    for imgName in inFiles:
        for i in range(1, 10):
            #Quantize calls:
            numCols = i
            outputName = os.path.splitext(imgName)[0] + "_" + str(numCols) + "_colors" + os.path.splitext(imgName)[1]
            cv2.imwrite(outputName, color_quantize(imgName, numCols))

        for i in range(30, 180, 30):
            #Hue Rot call:
            deg = i
            outputName = os.path.splitext(imgName)[0] + "_" + str(deg) + "_degrot" + os.path.splitext(imgName)[1]
            cv2.imwrite(outputName, hue_rotate(imgName, deg))

        for i in range(5):
            #Swap Id call:
            swapID = i
            outputName = os.path.splitext(imgName)[0] + "_" + str(swapID) + "_swapped" + os.path.splitext(imgName)[1]
            cv2.imwrite(outputName, swap_chans(imgName, swapID))
        
def swap_chans(imgName, swapId):
    img = cv2.imread(imgName)
    split = cv2.split(img)
    if swapId == 0:
        img = cv2.merge([split[1], split[2], split[0]])
    elif swapId == 1:
        img = cv2.merge([split[2], split[0], split[1]])
    elif swapId == 2:
        img = cv2.merge([split[1], split[0], split[2]])
    elif swapId == 3:
        img = cv2.merge([split[2], split[1], split[0]])
    elif swapId == 4:
        img = cv2.merge([split[0], split[2], split[1]])
    return img

def hue_rotate(imgName, degrees):
    '''Given an image filename, this function rotates the image 
       by the given number of degrees in the hue plane of 
       opencv's HSV space. It returns the resulting image'''
    img = cv2.imread(imgName)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    img_cpy = img.copy()
    for y in range(len(img)):
        for x in range(len(img[0])):
            img_cpy[y, x, 0] = (int(img_cpy[y, x, 0]) + int(degrees)) % 180
    return cv2.cvtColor(img_cpy, cv2.COLOR_HSV2BGR)
    


def color_quantize(imgName, numCols):
    '''Given an image filename, this function runs k-clustering on the image's 
       colors with k=numCols clusters and then sets ever pixel in a given cluster 
       to the centroid color vector of the cluster. It then returns the color quantied image.'''
    img = cv2.imread(imgName)
    # Reshape the image matrix to a lst of each idivid pixel 
    Z = img.reshape((-1, 3))
    # convert to np.float32
    Z = np.float32(Z)
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = numCols
    ret,label,center=cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))
    return res2


def search_res_wiki_summary(searchString, res=3, sent=2, lang="en"):
    '''Returns a 'sent' number sentence summary of top 'res' number 
       of texts from wikipedia page results from seaching 
       'searchString'. Default language is English.'''
    # Set language if it should not be the default:
    if lang != "en":
        wik.set_lang(lang)
        
    pgs = wik.search(searchString, results=res)
    summaries = []
    for pg in pgs: 
      # Create a starting string:
      text = 'According to Wikipedia, '
      # Si el idioma es espanol, tenemos una frase especial de empezar: 
      if lang == "es":
        text = 'Según Wikipedia, '
      # Get search results:
      text += wik.summary(pg, sentences=sent)
      summaries.append(text)
    return summaries

def rand_wiki_summary(lang="en"):
    '''Returns a 1 sentence summary of text from a 
    random wikipedia article. Default language is English.'''
    # Create a starting string:
    text = 'According to Wikipedia, '
    # Set language if it should not be the default:
    if lang != "en":
        wik.set_lang(lang)
        # Si el idioma es espanol, tenemos una frase especial de empezar: 
        if lang == "es":
            text = 'Según Wikipedia, '
    # Get random page:    
    rnd_pg_name = wik.random()
    text += wik.summary(rnd_pg_name, sentences=1)
    return text, rnd_pg_name
    

def rand_wiki_text(lang="en"):
    '''Returns a section of text from a 
    random wikipedia article. Default language is English.'''
    # Create a starting string:
    text = 'From the Wikipedia article '
    # Set language if it should not be the default:
    if lang != "en":
        wik.set_lang(lang)
        # Si el idioma es espanol, tenemos una frase especial de empezar: 
        if lang == "es":
            text = 'Desde el articulo de Wikipedia '
    # Get random page:    
    rnd_pg_name = wik.random()
    # Add the page title to the string:
    text += rnd_pg_name + '\n: '
    rnd_pg = wik.page(rnd_pg_name)
    n_secs = len(rnd_pg.sections)
    # If there is more than one section of this page, append the text of a random section: 
    if n_secs > 1:
        rnd_sec = rnd_pg.section(rnd_pg.sections[random.randint(0, n_secs - 2)])
        text += rnd_sec
    # Otherwise, the page is a stub and we can just append the entire page's content:
    else:
        text += rnd_pg.content
    return text


def Post_alg_art(inDir):
    inFiles = [os.path.join(inDir, f) for f in os.listdir(inDir) if ("_colors" not in f and "_swapped" not in f and "_degrot" not in f)]
    for imgName in inFiles:
        baseName = os.path.splitext(os.path.basename(imgName))[0]
        baseExt = os.path.splitext(os.path.basename(imgName))[1]
        api.PostUpdate(baseName, media=imgName)
        for i in range(5):
            time.sleep(1)
            api.PostUpdate(baseName + " swapped color channels " + str(i), media=os.path.join(inDir, baseName) + "_" + str(i) + "_swapped" + baseExt)
        for i in range(30, 180, 30):
            time.sleep(1)
            api.PostUpdate(baseName + " rotated hue " + str(i) + " degrees", media=os.path.join(inDir, baseName) + "_" + str(i) + "_degrot" + baseExt)
        for i in range(9, 0, -1):
            time.sleep(1)
            api.PostUpdate(baseName + " quantized to " + str(i) + " colors", media=os.path.join(inDir, baseName) + "_" + str(i) + "_colors" + baseExt)
        time.sleep(10)

def placeholder():
    '''A placeholder for random shit.'''
    # post status:
    api.PostUpdate('Hello World!')
    # Block User:
    api.CreateBlock(screen_name="KTHopkins")
    # Post picture (with url):
    api.PostUpdate('What are frogs?', media="https://dw8stlw9qt0iz.cloudfront.net/FHKzfst9humx0GtrBeGw3IGA-Oo=/2000x2000/filters:format(jpeg):quality(75)/curiosity-data.s3.amazonaws.com/images/content/thumbnail/standard/27aee7af-a3dc-4c67-e57f-7648839ecd18.png")
    # Get list of all friends:
    users = api.GetFriends(screen_name="Testbot36612540")
    print([u.screen_name for u in users])
    # Post random wiki sections:
    while(True):
        try:
            api.PostUpdates(rand_wiki_text(), continuation='\u2026')
        except twitter.error.TwitterError:
            pass
        time.sleep(5)
    # Post random wiki summaries:
    while(True):
        try:
            api.PostUpdates(rand_wiki_summary(), continuation='\u2026')
        except twitter.error.TwitterError:
            pass
        except wikipedia.exceptions.DisambiguationError:
            pass
        time.sleep(5)

if __name__ == "__main__":
    # Read in the Twitter credentials from a local JSON file: 
    credJson = "/media/dmac/83727f8f-39a4-41a3-93f7-420f8801cf3b/code/python_practice/dat/twitter_credentials.json"
    with open(credJson, "r") as credFile:
        creds = json.load(credFile)
    # Create a Twitter API Object for making calls:
    api = twitter.Api(consumer_key=creds["CONSUMER_KEY"],
                      consumer_secret=creds["CONSUMER_SECRET"],
                      access_token_key=creds["ACCESS_TOKEN"],
                      access_token_secret=creds["ACCESS_SECRET"])

    # while (True):
    #   try:
    #     summ, pgName = rand_wiki_summary(lang="es")
    #     # remove footnote citation brackets:
    #     summ = re.sub(r'\[\d+\]', '', summ)
    #     # remove anything after a period:
    #     summ = re.sub(r'\.[\S\s]*', r'.', summ)
    #     link = r"https://es.wikipedia.org/wiki/" + "_".join(pgName.split())
    #     print(summ)
    #     print(link)
    #     api.PostUpdates(summ + " " + link, continuation='\u2026')
    #   except twitter.error.TwitterError:
    #     pass
    #   except wik.exceptions.DisambiguationError:
    #     pass     
    #   time.sleep(300)


    # searchStrings = sys.argv[1:]
    # for searchString in searchStrings:
    #   summs = search_res_wiki_summary(searchString, res=1, sent=1, lang="es")
    #   for summ in summs:
    #     summ = re.sub(r'\[\d+\]', '', summ)
    #     summ = re.sub(r'\.[\S\s]*', r'. #RacistPresident', summ)
    #     api.PostUpdates(summ, continuation='\u2026')
    #     time.sleep(5)
       # print(summ + "\n\n\n")

    
    # random lines from a text:
    # intxt = sys.argv[1]
    # textList = read_txt(intxt)
    # while(True):
    #     randText = " ".join(return_random_text(textList, minstrlen=25, maxstrlen=50))
    #     api.PostUpdates(randText, continuation='\u2026')
    #     time.sleep(5)

    #Follow followers of a given user:
    users = api.GetFollowers(screen_name="KtownforAll", total_count=50)
    for user in users:
        api.CreateFriendship(screen_name=user.screen_name)
        print(user.screen_name)
        time.sleep(5)

    # create dumb memes:
    # textDir = sys.argv[1]
    # imgDir = sys.argv[2]
    # outDir = sys.argv[3]
    # while(True):
    #     create_dumb_memes(textDir, imgDir, outDir)

    
    


