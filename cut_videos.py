from cv2 import cv2
import glob

def getVideopath()->list:
    files = glob.glob('./video/*.avi')
    if(len(files) == 0):
        print("video files in mp4 format not found!")
        exit()
    return files


def cut(files:list):

    #files = getVideopath()

    cap = cv2.VideoCapture(files[0])

    count = 0
    flag = 1

    image_names = ""

    while cap.isOpened():
        ret, frame = cap.read()
        if flag==1:
            cv2.imwrite('./images/clean.jpg', frame)
            count += 30 # i.e. at 30 fps, this advances one second
            cap.set(cv2.CAP_PROP_POS_FRAMES, count)
            image_names += "/images/clean.jpg"  
            flag = 0
        else:

            if ret:
                cv2.imwrite('./images/frame{:d}.jpg'.format(count), frame)
                image_names += " /images/frame{:d}.jpg".format(count)
                count += 30 # i.e. at 30 fps, this advances one second
                cap.set(cv2.CAP_PROP_POS_FRAMES, count)
            else:
                cap.release()

                file = open("data.py", "w").write(str(image_names))
                
                return
