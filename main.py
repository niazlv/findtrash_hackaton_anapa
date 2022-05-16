import cv2 as cv
import numpy as np
import cut_videos


def trackbar(x, hsv):
    lower = (x, 30, 30)
    upper = (x + 35, 250, 250)
    mask = cv.inRange(hsv, lower, upper)
    white_pix = np.sum(mask == 255)
    black_pix = np.sum(mask == 0)
    dark_pix = int((black_pix*100)/(white_pix+black_pix))
    return {
        'white_pix': white_pix,
        'black_pix': black_pix,
        'dark_pix': dark_pix,
        'mask': mask
    }
status = -1

def getStatus()->int:
    return status

def garbage_status(d_standard, d_new):
    global status
    sum_percentage = 0
    for x in range(180):
        white_pix_standard = int(d_standard[x])
        white_pix_new = int(d_new[x])
        if white_pix_standard != 0:
            y = int(white_pix_new * 100 / white_pix_standard)
            if y > 200:
                y = 200
            sum_percentage += y

    average_percentage = abs((int(sum_percentage / 180) - 100))

    #status = average_percentage//20 + 1
    #print(status)
    if average_percentage <= 20:
        status = 1
    elif 20 < average_percentage <= 40:
        status = 2
    elif 40 < average_percentage <= 60:
        status = 3
    elif 60 < average_percentage <= 80:
        status = 4
    elif 80 < average_percentage <= 100:
        status = 5
    print(average_percentage)
    print("Загрязнение - "+str(status))

def get_garbage(filepath:str):
    #Нарезаем видео
    cut_videos.cut([filepath])
    #Сохраняем названия фреймов
    data = open("data.py", "r").read().replace('\n', '').split(" ")
     
    img_standard = cv.imread(data[0][1:])
    img_new = cv.imread(data[-1][1:])
    #Вызываем окно селектора для получения координат окна
    r = cv.selectROI(img_standard)
    #Уничтожаем окно селектора
    cv.destroyWindow("ROI selector")
    #формируем и вырезаем картинку из картинки
    img_standard = img_standard[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    img_standard_copy = img_standard
    img_new = img_new[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    cv.imwrite('img_last.png', img_new)
    print(r[1], r[1]+r[3], r[0], r[0]+r[2])

    dict_standard, dict_new = {}, {}

    


    img_standard_hsv = cv.cvtColor(img_standard, cv.COLOR_BGR2HSV)
    img_new_hsv = cv.cvtColor(img_new, cv.COLOR_BGR2HSV)

    for i in range(180):
        dict_standard[i] = trackbar(i, img_standard_hsv)['white_pix']
        dict_new[i] = trackbar(i, img_new_hsv)['white_pix']

    garbage_status(dict_standard, dict_new)

    num_test = 90

    img_standard_result = cv.bitwise_and(img_standard, img_standard, mask=trackbar(num_test, img_standard_hsv)['mask'])
    img_standard_result_copy = cv.bitwise_and(img_standard_copy, img_standard_copy)
    img_new_result = cv.bitwise_and(img_new, img_new, mask=trackbar(num_test, img_new_hsv)['mask'])
    cv.imwrite('result_standard_preview.png', img_standard_result_copy)

    cv.imwrite('result_standard.png', img_standard_result)
    cv.imwrite('result_new.png', img_new_result)

    cv.imwrite('result_standard_mask.png', trackbar(num_test, img_standard_hsv)['mask'])
    cv.imwrite('result_new_mask.png', trackbar(num_test, img_new_hsv)['mask'])

#get_garbage()



