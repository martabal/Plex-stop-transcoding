from TautulliApiHandler import TautulliApiHandler
import datetime

import time
from os import environ

### PUT YOUR VARIABLES ###
def GetTautInfo():


    if environ.get('TAUTULLI_IP') is None or environ.get('TAUTULLI_IP') == ""  :
        print("You have to enter the tautulli's IP")
        quit()
    
    if environ.get('TAUTULLI_PORT') is None or environ.get('TAUTULLI_PORT') == "" :
        print("You have to enter the port of Tautulli")
        quit()

    if  environ.get('TAUTULLI_API') is None or environ.get('TAUTULLI_API') == "" :
        print("You have to enter the API of Tautulli")
        quit()
 
    tautulliIp   = environ.get('TAUTULLI_IP')                     # IP Address of Tautulli
    tautulliPort = environ.get('TAUTULLI_PORT')
                            # Port of Tautulli
    tautulliApi  = environ.get('TAUTULLI_API')
    # Message to display to a user of a blacklisted IP
    
    blackListMsg = environ.get('BLACKLISTMSG', default = "-TRANSCODE-")
 


    concurrentMsg = environ.get('CONCURRENTMSG', default ="PLEX TRANSCODE ENFORCER - YOU ARE NOT ALLOWED TO TRANSCODE STREAMS" )


    return tautulliIp, tautulliPort, tautulliApi, blackListMsg, concurrentMsg



def GetConcSettings():
    try:
        f = open("authorized.txt", "r")
        lines = f.read().splitlines() # Use this rather than readlines so we remove the newline character
        f.close()
        lines = [int(i) for i in lines]

        return lines
    except:
        pass

def EnforceConcurrent(tActivitySessions, tapi, concurrentMsg,web,mediaplayer,sd):
    try:
        concSettings = GetConcSettings()

        dataByUser = {}
        # Loop through each session and add to a dictionary where key is the username
        for session in tActivitySessions:
            if(session["user"] in dataByUser):
                # User is already in the dictionary so append to that users array
                dataByUser[session["user"]].append(session)
            else:
                # User isnt in dictionary so add key data pair with username as key and an ampty array as data
                dataByUser[session["user"]] = []
                dataByUser[session["user"]].append(session) # Append that session to the array of that user

        # By this point we have a dictionary of current users with their apropriate sessions
        for cle,valeur in dataByUser.items():



            print(valeur)
            for j in range(len(valeur)) :

                userid = valeur[j].get('user_id')
                stream_video_resolution = valeur[j].get('stream_video_resolution')
                name = valeur[j].get('friendly_name')
                if name == "" :
                    name = str(valeur[j].get('user_id'))


                if userid not in concSettings:


                    print(name + " : User unauthorized")

                    if(mediaplayer == True or web == True):
                        if(valeur[j].get('product') == 'Plex Media Player' and mediaplayer == True) :
                            concurrentMsg = "PLEX ENFORCER - YOUR MEDIA PLAYER IS DEPRECATED"
                        if(valeur[j].get('product') == 'Plex Web' and web == True) :
                            concurrentMsg = "PLEX ENFORCER - YOUR ARE NOT AUTHORIZED TO USE PLEX WEB"
                        tapi.TerminateSession(valeur[j].get('session_key'), concurrentMsg)
                        print(name + " : Terminating sessions")
                        EnforcementLogger(valeur[j].get('friendly_name'), "transcode")

                    elif(valeur[j].get('video_decision') == 'transcode' and valeur[j].get('state') != 'paused' and (( sd == True) and (valeur[j].get(stream_video_resolution) != 'sd' ) ) ):

                        tapi.TerminateSession(valeur[j].get('session_key'), concurrentMsg)
                        print(name + " : Terminating sessions")
                        EnforcementLogger(valeur[j].get('friendly_name'), "transcode")

                else :
                    print(name + " : User authorized")





    except:
        pass



def EnforcementLogger(message, reason):
    try:
        now = datetime.datetime.now()
        preStringDate = now.strftime("%Y-%m-%d %H:%M:%S")

        if(reason == "transcode") :
            f = open("enforce_log.txt", "a")
            f.write(preStringDate  + " : " + message + "\n")
            f.close()
        else :
            f = open("multiple_streams.txt", "a")
            f.write(reason  + " : " + message + "\n")
            f.close()

    except:
        print("There was a problem logging the error")
        pass

if __name__ == "__main__":
    print("\n")
    mediaplayer = False
    web = False
    sd = False

   
    tIP, tPORT, tAPIKEY, blackListMsg, concurrentMsg = GetTautInfo()
    tapi = TautulliApiHandler(tIP, tPORT, tAPIKEY)
    tActivityData = tapi.GetActivity()
    if(int(tActivityData["stream_count"]) > 0):
        print("There are currently " + str(tActivityData["stream_count"]) + " streams active")





        EnforceConcurrent(tActivityData["sessions"], tapi, concurrentMsg,web,mediaplayer,sd) # Check and Enforce Concurrent Limits

    else:
        print("No streams found")

        
