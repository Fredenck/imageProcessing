import numpy as np
import cv2
import os
import sys,traceback
import getopt
import dipUtil

def findName (files,img):
    for i in files:
        if i[0:9]==img:
            return i
    return '' 

def overlayImg(img1,img2, x_offset, y_offset):
    img1= cv2.imread(img1, cv2.IMREAD_REDUCED_GRAYSCALE_2)
    img2 = cv2.imread(img2, cv2.IMREAD_REDUCED_GRAYSCALE_2)
    img1 = dipUtil.maskImage(img1)
    img2 = dipUtil.maskImage(img2)
    transformImg1 = dipUtil.transformImage(img1)
    transformImg2 = dipUtil.transformImage(img2)
    pt1 = dipUtil.findHorizontalPoints(transformImg1)[0]
    pt2 = dipUtil.findHorizontalPoints(transformImg2)[0]
    offset = np.subtract(pt1,pt2)#offset is (x,y)
    y = offset[1]-y_offset#y_offset is going north(math coords), the offset itself go south when positive(img coords)
    x = offset[0]+x_offset
    shiftxImg2 = np.roll(transformImg2, x, axis=1)
    shiftxyImg2 = np.roll(shiftxImg2, y, axis=0)
    shiftxyImg2RGB = cv2.cvtColor(shiftxyImg2, cv2.COLOR_GRAY2RGB)
    colorImg1 = cv2.cvtColor(transformImg1, cv2.COLOR_GRAY2RGB)
#     colorImg2 = np.divide(shiftxyImg2RGB, 2)
    h, w, c=shiftxyImg2RGB.shape    
    for i in range(h-1):
        for j in range(w-1):
            for k in range(c):
                shiftxyImg2RGB[i][j][k] = int(shiftxyImg2RGB[i][j][k]/5)
    finalImg = np.add(colorImg1, shiftxyImg2RGB)#overlapping
    h, w, c=finalImg.shape
    for i in range(h-1):
        for j in range(w-1):
            for k in range(c):
                if finalImg[i][j][k]>255:
                    finalImg[i][j][k]=255
    return finalImg  

def main(argv):
    inImgPath = "c:\\proj\\in_images"
    outImgPath = "c:\\proj\\out_images"
    outDataPath = "c:\\proj\\out_data"
    helpMsg = 'dip.py -i <inImgDir> -o <outImgDir> -d <outDataDir> -1 <img1> -2 <img2> -x <shift img1 in x dir> -y <shift img1 in y dir>'
    x_offset = 0
    y_offset = 0
    try:
        opts, args = getopt.getopt(argv,"hi:o:d:1:2:x:y:",["inImgDir=","outImgDir=","outDataDir"])
    except getopt.GetoptError:
        print(helpMsg)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(helpMsg)
            sys.exit()
        elif opt in ("-i", "--inImgDir"):
            inImgPath = arg
        elif opt in ("-o", "--outImgDir"):
            outImgPath = arg
        elif opt in ("-d", "--outDataDir"):
            outDataPath = arg
        elif opt in ("-1", ""):
            img1 = arg
        elif opt in ("-2", ""):
            img2 = arg
        elif opt in ("-y", ""):
            y_offset = arg
        elif opt in ("-x", ""):
            x_offset = arg
    print( 'Input img dir is ', inImgPath)
    print( 'Output img dir is ', outImgPath)
    print( 'Output data dir is ', outDataPath)
    print( 'img1 is ', img1)
    print( 'img2 is ', img2)
    print( 'x offset is', x_offset)
    print( 'y offset is', y_offset)
    x_offset = int(x_offset)
    y_offset = int(y_offset)
    #open input image dir (inImgPath)
    files = os.listdir(inImgPath)
    timestamp = dipUtil.getIso8601Datetime()
    outImgDirName = os.path.join(outImgPath,'out_images_'+timestamp)
    if not os.path.exists(outImgDirName):
        os.makedirs(outImgDirName)
    #open input files
    name1 = findName(files, img1)
    name2 = findName(files, img2)
    if name1=='':
        print('img1('+img1+')not found')
        sys.exit()
    if name2 =='':
        print('img2('+img2+') not found')
        sys.exit()
    img1Path = inImgPath+'\\'+name1
    img2Path = inImgPath+'\\'+name2
    oImg = overlayImg(img1Path, img2Path, x_offset, y_offset)
    #output overlayed images
    outImgDirName = os.path.join(outImgPath,'out_images_'+timestamp)
    if not os.path.exists(outImgDirName):
        os.makedirs(outImgDirName)
    r = img1+'__'+img2+ '.bmp'
    output = cv2.imwrite(outImgDirName+"\\"+r, oImg)

if __name__ == "__main__":
   main(sys.argv[1:])
