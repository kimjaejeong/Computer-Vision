# (1) 기하학 처리
#- 오른쪽 90도 회전
#- 이동 --> 상하/좌우
#- 축소 --> 배율(2/4/8....)
#- 확대 --> 배율(2/4)
#- (선택) 회전 --> 각도 입력(삼각함수 공식 들어감)

# [화소점 처리]에 다음 메뉴를 추가하고, 구현하시오.
# (1) 밝게하기
# (2) 어둡게하기
# (3) 영상 곱셈
# (4) 영상 나눗셈
# (5) 화소값 반전 : 0-->255, 1->254 ~~~~
# (6) 이진화(=흑백 영상) : Black/White 2 값으로만 구성된 영상
# (7) 입력/출력 영상의 평균값 구하기 : 출력은 messagebox로
# (8) <선택> Posterizing, Gamma 보정, 명암 대비 스트레칭

from tkinter import *
from tkinter.simpledialog import *
from tkinter.filedialog import *
import math
import os
import os.path


###################
### 함수 선언부 ###
###################
# 메모리를 할당해서 리스트(참조)를 반환하는 함수
def malloc(h, w, initValue = 0):  # 값을 안받으면 default 0으로 처리.
    retMemory = []
    for _ in range(h):
        tmpList = []
        for _ in range(w):
            tmpList.append(initValue)
        retMemory.append(tmpList)
    return retMemory

# 파일을 메모리로 로딩하는 함수
def loadImage(fname):
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    fsize = os.path.getsize(fname)  # 파일의 크기(바이트)
    inH = inW = int(math.sqrt(fsize))  # 핵심 코드 -> 정사각형이므로 루트를 씌우면 가로와 높이가 나옴.

    ## 입력영상 메모리 확보 ## - 512 x 512를 0으로 초기화 시킴.
    inImage = []  # load가 계속 될 수 있기 때문에 초기화 시키는 용도로 사용.
    for _ in range(inH):
        tmpList = []
        for _ in range(inW):
            tmpList.append(0)
        inImage.append(tmpList)
    # 파일 --> 메모리
    with open(filename, 'rb') as rfp:  # 우리는 binary 이므로 rb 사용.(이미지이기 때문에 binary) cf. txt는 r
        for i in range(inH):
            for k in range(inW):
                inImage[i][k] = int(ord(rfp.read(1)))  # 1바이트만 읽는다.
    print(inH, inW)
    print(inImage[80][70])


# 파일을 선택해서 메모리로 로딩하는 함수
def openImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    filename = askopenfilename(parent=window,
                               filetypes=(("RAW 파일", "*.raw"), ("모든 파일", "*.*")))
    if filename == '' or filename == None:
        return
    loadImage(filename)
    equalImage()

import struct
def saveImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    saveFp = asksaveasfile(parent = window, mode = 'wb',
            defaultextension="*.raw", filetypes=(("RAW 파일", "*.raw"), ("모든 파일", "*.*")))
    if saveFp == '' or saveFp == None:
        return
    for i in range(outH):
        for k in range(outW):
            saveFp.write(struct.pack('B', outImage[i][k]))
    saveFp.close()



def displayImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    if canvas != None:  # 예전에 실행한 적이 있다.
        canvas.destroy()  # canvas를 뽑아냄.
    ## 화면 크기를 조절 -> window -> canvas -> paper를 만듬
    window.geometry(str(outH) + 'x' + str(outW))  # '512 x 512'
    canvas = Canvas(window, height=outH, width=outW)
    paper = PhotoImage(height=outH, width=outW)  # 빈 종이 -> PhotoImage로 가져옴.
    canvas.create_image((outH // 2, outW // 2), image=paper,
                        state='normal')  # 종이를 붙이는 데 정중앙 갖다 놓기만 함.(밑에 canvas.pack()에서는 사진을 찍는다)
    ## 출력영상 --> 화면에 한점씩 찍어
    # for i in range(outH):  # display는 outH로 찍어야 함
    #     for k in range(outW):
    #         r = g = b = outImage[i][k]  # Gray scale이기 때문에 r = g = b로 표현함.
    #         paper.put("#%02x%02x%02x" % (r, g, b), (k, i))  # 색 표시 할 때 #RRGGBB 에서 각 글자는 0~F까지   %02는 두칸 x
    ## 성능 개선 -> 위 보다 속도가 확연히 빨라짐.
    rgbStr = '' # 전체 픽셀의 문자열을 저장
    for i in range(outH):
        tmpStr = ''
        for k in range(outW):
            r = g = b = outImage[i][k]
            tmpStr += ' #%02x%02x%02x' % (r,g,b)  # 한칸 띄워야 함. 아니면 구분을 못함.
        rgbStr += '{' + tmpStr + '} ' # 중괄호끼리도 붙어 있으면 구분을 못함.
    paper.put(rgbStr)



    canvas.bind("<Button-1>", mouseClick)
    canvas.bind("<ButtonRelease-1>", mouseDrop)
    canvas.pack(expand=1, anchor=CENTER)  # 위의 canvas.pack()은 중앙에 점을 찍는다.


#################################################
#### 컴퓨터 비전(영상처리) 알고리즘 함수 모듈 ####
#################################################
## outImage는 알고리즘에 따라 사이즈도 정해질 수 있음.

# 동일영상 알고리즘
def equalImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = inImage[i][k]
    displayImage()


# 밝게하기
def addImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    value = askinteger("밝게하기", "밝게할 값~~>", minvalue=1, maxvalue=255)  # 최소 1, 최대 255
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = inImage[i][k] + value
            if outImage[i][k] >= 255:
                outImage[i][k] = 255
    displayImage()


# 어둡게하기

def subImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    value = askinteger("어둡게하기", "어둡게할 값~~>", minvalue=1, maxvalue=255)  # 최소 1, 최대 255
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = inImage[i][k] - value
            if outImage[i][k] < 0:
                outImage[i][k] = 0
    displayImage()


# 영상 곱셈
def multiImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    value = askinteger("영상 곱하기", "영상 곱하게 할값~~>", minvalue=1, maxvalue=255)  # 최소 1, 최대 255
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = (inImage[i][k] * value)
            if outImage[i][k] > 255:
                outImage[i][k] = 255
    displayImage()


# 영상 나눗셈
def divImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    value = askinteger("영상 나누기", "영상 나누게 할 값~~>", minvalue=1, maxvalue=255)  # 최소 1, 최대 255
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = inImage[i][k] // value
            if outImage[i][k] < 0:
                outImage[i][k] = 0
    displayImage()


# 화소값 반전
def reverseImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = 255 - inImage[i][k]
    displayImage()


# 이진화(=흑백 영상)
def bwImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    # 평균을 기준으로 잡자.
    sum = 0
    for i in range(inH):
        for k in range(inW):
            sum += inImage[i][k]
    avg = sum // (inW * inH)
    for i in range(inH):
        for k in range(inW):
            if inImage[i][k] > avg:
                outImage[i][k] = 255
            else:
                outImage[i][k] = 0
    displayImage()


# 입력/출력 영상의 평균값 구하기
def avgImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    sum = 0
    for i in range(inH):
        for k in range(inW):
            sum += inImage[i][k]
    avg = sum / (inH * inW)
    messagebox.showinfo("평균값은 얼마인가요?", avg)
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = int(avg)
    ## 한 사진에 똑같은 숫자들이 입력되면 한 색이 나온다.
    displayImage()

# 파라볼라 알고리즘 with LUT
def paraImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########

    # LUT 활용 - 연산 속도가 훨씬 빨라짐.(실무에서 많이 사용)
    LUT = [0 for _ in range(256)]  # LUT가 256개 0으로 초기화
    for input in range(256):
        LUT[input] = int(255 - 255 * math.pow(input / 128 - 1, 2))
    ## LUT를 먼저 다 만들어준다.

    for i in range(inH):
        for k in range(inW):
            input = inImage[i][k]
            outImage[i][k] = LUT[inImage[i][k]]

    displayImage()

def upDownImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    for i in range(inH):
        for k in range(inW):
            outImage[inH - i - 1][k] = inImage[i][k]
    ## 상하가 바뀌었다는 것은 같은 열에서 맨 위의 값과 맨 밑의 값이 바뀌어야 한다. 따라서,
    ##열은 변화가 없고, 행 값만 역으로 해주면 된다. inH - i - 1 값을 취하면 상하가 바뀌게 된다.
    displayImage()

# 화면이동 알고리즘
def moveImage():
    global panYN
    panYN = True  # 마우스가 먹음
    canvas.configure(cursor = 'mouse')

def mouseClick(event):
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global sx, sy, ex, ey, panYN
    if panYN == False:   # 진행하지 말아라. 마우스 클릭 해봤자 아무 반응도 안함.
        return
    sx = event.x; sy = event.y   # 클릭해라.

def mouseDrop(event):
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    global sx, sy, ex, ey, panYN
    if panYN == False:   # 진행하지 말아라. 마우스 클릭 해봤자 아무 반응도 안함.
        return
    ex = event.x; ey = event.y
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    mx = sx - ex; my = sy - ey   # x, y에 대한 이동 양
    for i in range(inH):
        for k in range(inW):
            if 0 <= i-my < outW and 0 <= k-mx < outH:
                outImage[i-my][k-mx] = inImage[i][k]
    panYN = False
    displayImage()

#영상 축소 알고리즘
def zoomOutImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    value = askinteger("축소", "값~~>", minvalue=2, maxvalue=16)  # 최소 1, 최대 255
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH//value
    outW = inW//value
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    # backwarding 기법
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] = inImage[i*value][k*value]
    displayImage()

    # forwarding 기법
    #위 보다 성능이 덜 좋다. 위는 outH로 돌리기 때문에 훨씬 빨리 돈다.
    # for i in range(inH):
    #     for k in range(inW):
    #         outImage[i//value][k//value] = inImage[i][k]
    # displayImage()

#영상 축소 알고리즘(평균변환)
def zoomOutImage2():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    value = askinteger("축소", "값~~>", minvalue=2, maxvalue=16)  # 최소 1, 최대 255
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH//value
    outW = inW//value
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    for i in range(inH):
        for k in range(inW):
            outImage[i//value][k//value] += inImage[i][k]
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] //= (value*value)

    displayImage()




#영상 확대 알고리즘
def zoomInImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    value = askinteger("확대", "값~~>", minvalue=2, maxvalue=4)  # 최소 1, 최대 255
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH * value
    outW = inW * value
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########

    # backwarding 기법
    for i in range(outH):
        for k in range(outW):
            outImage[i][k] = inImage[i//value][k//value]
    displayImage()


    # forwarding 기법
    # for i in range(inH):
    #     for k in range(inW):
    #         outImage[i*value][k*value] = inImage[i][k]
    # displayImage()

# 영상 확대 알고리즘 (양선형 보간) -> 영상 품질을 향상시킬 수 있음.
def zoomInImage2():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    value = askinteger("확대", "값~~>", minvalue=2, maxvalue=4)  # 최소 1, 최대 255
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH * value
    outW = inW * value
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    rH, rW, iH, iW = [0] * 4 # 실수위치 및 정수 위치   / real integer
    x,y = 0, 0 # 실수와 정수의 차이값
    C1,C2,C3,C4 = [0] * 4 # 결정할 위치(N)의 상하좌우 픽셀
    for i in range(outH):
        for k in range(outW):
            rH = i / value; rW = k / value    # 확대하기 때문에 나눠야 함.
            iH = int(rH); iW = int(rW)   # 나눈 값을 정수로 나타냄.
            x = rW - iW; y = rH - iH  #
            if 0 <= iH < inH-1 and 0 <= iW < inW-1:
                C1 = inImage[iH][iW]
                C2 = inImage[iH][iW + 1]
                C3 = inImage[iH+1][iW+1]
                C4 = inImage[iH+1][iW]
                newValue = C1*(1-y)*(1-x) + C2*(1-y)*x + C3*y*x + C4*y*(1-x)
                outImage[i][k] = int(newValue)
    displayImage()

# 영상 회전 알고리즘
def rotateImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    angle = askinteger("회전", "값~~>", minvalue=1, maxvalue=360)
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    radian = angle * math.pi / 180
    for i in range(inH):
        for k in range(inW):
            xs = i; ys = k;
            xd = int(math.cos(radian) * xs - math.sin(radian) *ys)
            yd = int(math.sin(radian) * xs + math.sin(radian) *ys)
            if 0 <= xd < inH and 0 <= yd < inW :
                outImage[xd][yd] = inImage[i][k]

    displayImage()

# 히스토그램 -> 영상 그래프를 시각적으로 확인하기 위함.
import matplotlib.pyplot as plt
def histoImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    inCountList = [0] * 256
    outCountList = [0] * 256

    for i in range(inH):
        for k in range(inW):
            inCountList[inImage[i][k]] += 1

    for i in range(outH):
        for k in range(outW):
            outCountList[outImage[i][k]] += 1

    plt.plot(outCountList)
    plt.plot(inCountList)
    plt.show()

# 스트레칭 알고리즘(명암)
def stretchImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    maxVal = minVal = inImage[0][0]
    for i in range(inH):
        for k in range(inW):
            if inImage[i][k] < minVal:
                minVal = inImage[i][k]
            elif inImage[i][k] > maxVal:
                maxVal = inImage[i][k]

    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = int(((inImage[i][k] - minVal) / (maxVal - minVal)) * 255)
    displayImage()

def endinImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    maxVal = minVal = inImage[0][0]
    for i in range(inH):
        for k in range(inW):
            if inImage[i][k] < minVal:
                minVal = inImage[i][k]
            elif inImage[i][k] > maxVal:
                maxVal = inImage[i][k]

    minAdd = askinteger("최소", "최소추가~~>", minvalue=0, maxvalue=255)
    maxAdd = askinteger("최대", "최소감소~~>", minvalue=0, maxvalue=255)

    minVal += minAdd
    maxVal -= maxAdd

    for i in range(inH):
        for k in range(inW):
            value = int((inImage[i][k] - minVal) / (maxVal - minVal)) * 255
            if value <0:
                value = 0
            elif value >255:
                value = 255
            outImage[i][k] = value
    displayImage()

# 평활화 - 강사님 방법
def smoothImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    histo = [0] * 256; sumHisto = [0] * 256; normalHisto =[0] * 256
    # 1. 빈도 수 조사
    for i in range(inH):
        for k in range(inW):
            histo[inImage[i][k]] += 1
    # 2. 누적 히스토그램 생성
    sValue = 0
    for i in range(len(histo)):
        sValue += histo[i]  # 누적 값. 계속 합쳐짐.
        sumHisto[i] = sValue
    # 3. 정규화 누적 히스토그램
    for i in range(len(sumHisto)):
        normalHisto[i] = int(sumHisto[i] / (inW * inH) * 255)
        ## inW * inH는 총 픽셀 수
    # 4. 영상처리
    for i in range(inH):
        for k in range(inW):
            outImage[i][k] = normalHisto[inImage[i][k]]

    displayImage()

# 엠보싱 처리
def embossImage():
    global window, canvas, paper, filename, inImage, outImage, inW, inH, outW, outH
    ## 중요! 코드, 출력영상 크기 결정 ##
    outH = inH;
    outW = inW
    ###################################
    outImage = []
    outImage = malloc(outH, outW)
    ########진짜 컴퓨터 비전 알고리즘 ########
    MSIZE = 3
    mask = [ [-1, 0, 0],
             [ 0, 0, 0],
             [ 0, 0, 1] ]

    ## 임시 입력영상 메모리 확보 -> Input 메모리 확보를 위한.
    tmpInImage = malloc(inH + (MSIZE - 1), inW + (MSIZE -1), 127)  # 127은 중간값 / 마스크에 따라 바깥 처리를 달리한다.
    tmpOutImage = malloc(outH, outW)
    ## 원 입력 ~~> 임시 입력
    for i in range(inH):
        for k in range(inW):
            tmpInImage[i+MSIZE//2][k+MSIZE//2] = inImage[i][k]   # 바깥 쪽 값 입력

    ## 회선연산
    for i in range(MSIZE//2, inH + MSIZE//2):   # 큰 틀이 주가 아니라, 더 안쪽의 값이 inputImage임
        for k in range(MSIZE//2, inW + MSIZE//2):
            # 각 점을 처리
            S = 0.0# S는 누적값
            for m in range(0, MSIZE):
                for n in range(0, MSIZE):
                    S += mask[m][n] * tmpInImage[i + m - MSIZE//2][k + n - MSIZE//2]
            tmpOutImage[i-MSIZE//2][k-MSIZE//2] = S
    ## 127 더하기 -> 선택해서 진행.
    for i in range(outH):
        for k in range(outW):
            tmpOutImage[i][k] += 127
    ## 임시 출력 --> 원 출력
    for i in range(outH):
        for k in range(outW):
            value = tmpOutImage[i][k]
            if value > 255:
                value = 255
            elif value < 0:
                value = 0
            outImage[i][k] = int(value)
    displayImage()
######################
### 전역변수 선언부 ###
######################
inImage, outImage = [], []
## inImage는 사진 로드 했을 때의 값
inH, inW, outH, outW = [0] * 4
window, canvas, paper = None, None, None
filename = ""  # filename은 계속 가지고 다닐 것임.
panYN = False
sx,sy,ex,ey = [0] * 4

###################
### 메인 코드부 ###
###################
# 메인 코드  부분
window = Tk()
window.geometry("500x500")
window.title("컴퓨터 비전(딥러닝 기법) ver 0.03")

## 마우스 이벤트
window.bind("")

mainMenu = Menu(window)
window.config(menu=mainMenu)

fileMenu = Menu(mainMenu)
mainMenu.add_cascade(label="파일", menu=fileMenu)
fileMenu.add_command(label="파일 열기", command=openImage)
fileMenu.add_separator()
fileMenu.add_command(label="파일 저장", command=saveImage)

comVisionMenu1 = Menu(mainMenu)
mainMenu.add_cascade(label="화소점 처리", menu=comVisionMenu1)
comVisionMenu1.add_command(label="밝게하기", command=addImage)
comVisionMenu1.add_command(label="어둡게하기", command=subImage)
comVisionMenu1.add_command(label="영상 곱셈", command=multiImage)
comVisionMenu1.add_command(label="영상 나눗셈", command=divImage)
comVisionMenu1.add_command(label="화소값 반전", command=reverseImage)
# comVisionMenu1.add_command(label="흑백 영상", command=bwImage)
comVisionMenu1.add_command(label="입출력 평균값 영상", command=avgImage)
comVisionMenu1.add_command(label="파라볼라", command=paraImage)
# comVisionMenu1.add_command(label="Posterizing", command=posterImage)
# comVisionMenu1.add_command(label="Gamma 보정", command=gammaImage)
# comVisionMenu1.add_command(label="명암 대비 스트레칭", command=)

comVisionMenu2 = Menu(mainMenu)
mainMenu.add_cascade(label="화소(통계)", menu=comVisionMenu2)
comVisionMenu2.add_command(label="이진화", command=bwImage)
comVisionMenu2.add_command(label="축소(평균변환)", command=zoomOutImage2)
comVisionMenu2.add_command(label="확대(양선형보간)", command=zoomInImage2)
comVisionMenu2.add_separator()
comVisionMenu2.add_command(label = "히스토그램", command=histoImage)
comVisionMenu2.add_command(label = "명암대비", command=stretchImage)
comVisionMenu2.add_command(label = "End-In탐색", command=endinImage)
comVisionMenu2.add_command(label = "평활화", command=smoothImage)


comVisionMenu3 = Menu(mainMenu)
mainMenu.add_cascade(label="기하학 처리", menu=comVisionMenu3)
comVisionMenu3.add_command(label="상하반전", command=upDownImage)
comVisionMenu3.add_command(label="이동", command=moveImage)
comVisionMenu3.add_command(label="확대", command=zoomInImage)
comVisionMenu3.add_command(label="축소", command=zoomOutImage)
comVisionMenu3.add_command(label="회전", command=rotateImage)

comVisionMenu4 = Menu(mainMenu)
mainMenu.add_cascade(label="화소영역처리", menu=comVisionMenu4)
comVisionMenu4.add_command(label="엠보싱", command=embossImage)

window.mainloop()

