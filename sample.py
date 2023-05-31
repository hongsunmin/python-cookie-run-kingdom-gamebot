from gettext import find
from inspect import stack
import os, logging, re
from time import sleep
from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage

import easyocr

class CookieRunKingdom:
    def __init__(self):
        logging.basicConfig(filename='robot.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - [%(levelname)s] (%(filename)s:%(lineno)d) > %(message)s')
        logging.info('game robot init.')
        self._reader = easyocr.Reader(['ko', 'en'], gpu=True)
        self._connectDevice()
    
    def _connectDevice(self):
        logging.debug('connecting device...')
        self._device = MonkeyRunner.waitForConnection(None)
        logging.debug('connected to device.')
    
    def _loadImageFromFile(self, path):
        image = MonkeyRunner.loadImageFromFile(path)
        return image
    
    def ready(self):
        runComponent = 'com.devsisters.ck/com.devsisters.plugin.OvenUnityPlayerActivity'
        
        # check foreground game process
        started = False
        while True:
            focusApp = self._device.shell("dumpsys window windows | grep -E 'mCurrentFocus|mFocusedApp'")
            p = re.compile('mCurrentFocus=.*{(.*)}')
            m = p.search(focusApp)
            print(m)
            if m is None or m.group(1).find(runComponent) == -1:
                logging.info('app is not running. start %s' % runComponent)
                # self._device.startActivity(component=runComponent)
                os.system('/Users/a201510003/Library/Android/sdk/platform-tools/adb shell am start -a android.intent.action.MAIN -n %s' % runComponent)
                logging.info('started app.')
                started = True
            else:
                break
        return started
    
    def kill(self):
        runPackage = 'com.devsisters.ck'

        os.system('/Users/a201510003/Library/Android/sdk/platform-tools/adb shell am force-stop %s' % runPackage)
    
    def snapshot(self, capture=True):
        if capture or hasattr(self, '_lastSnapshot') == False:
            logging.debug('take snapshot.')
            self._lastSnapshot = self._device.takeSnapshot()
        else:
            logging.debug('last snapshot.')
        return self._lastSnapshot
    
    def touch(self, x, y):
        try:
            self._device.touch(x, y, MonkeyDevice.DOWN_AND_UP)
            logging.debug('touched (%d, %d)' % (x, y))
        except:
            logging.error('broken connection. re-connect device...')
            # self._device.reboot("None")
            self._connectDevice()
            logging.info('re-connected device')
        sleep(2)
    
    def home(self):
        self._device.press('KEYCODE_HOME', MonkeyDevice.DOWN_AND_UP)
        sleep(3)
    
    def dragUp(self):
        self._device.drag((1700, 380), (1700, 1300), 1.0, 10)
        sleep(2)

    def dragDown(self):
        self._device.drag((1700, 1300), (1700, 680), 1.0, 10)
        sleep(2)
    
    def findGreen(self, start = 400, capture=True):
        image = self.snapshot(capture)
        for y in range(start, 1439, 1):
            a, r, g, b = image.getRawPixel(2150, y)
            if r > 120 and r < 130 and g > 200 and g < 210 and b < 15:
                return (2150, y)
        return None
    
    def stock1(self, capture=True):
        self.saveSubSnapshot("tempstock1.png", (1400, 50, 165, 50), capture)
        sleep(1)
        result = self._reader.readtext("tempstock1.png")
        if len(result) == 1:
            text = result[0][1]
            try:
                logging.debug('stock1=%s' % text)
                return int(text)
            except ValueError:
                return -1
        return -1
    
    def stock2(self, y, capture=True):
        self.saveSubSnapshot("tempstock2.png", (1739, y - 38, 62, 43), capture)
        sleep(1)
        result = self._reader.readtext("tempstock2.png")
        if len(result) == 1:
            text = result[0][1]
            try:
                logging.debug('stock2=%s' % text)
                return int(text)
            except ValueError:
                return -1
        return -1
    
    def storeName(self, capture=True):
        self.saveSubSnapshot("tempstock2StoreName.png", (630, 65, 615, 90), capture)
        sleep(3)
        result = self._reader.readtext("tempstock2StoreName.png")
        if len(result) == 1:
            text = result[0][1]
            logging.debug('stock2StoreName=%s' % text)
            return text
        return None
    
    def goodsName(self, y, capture=True):
        self.saveSubSnapshot("tempstock2GoodsName.png", (1940, y - 305, 440, 60), capture)
        sleep(3)
        result = self._reader.readtext("tempstock2GoodsName.png")
        if len(result) == 1:
            text = result[0][1]
            logging.debug('stock2GoodsName=%s' % text)
            return text
        return None
    
    def saveSnapshot(self, path):
        snapshot = self.snapshot()
        snapshot.writeToFile(path, 'png')
        return snapshot

    def saveSubSnapshot(self, path, rect, capture=True):
        snapshot = self.snapshot(capture).getSubImage(rect)
        snapshot.writeToFile(path, 'png')
        return snapshot
    
    def sameAsImage(self, path, rect, capture=True, percent=1.0):
        image = self._loadImageFromFile(path)
        snapshot = self.snapshot(capture).getSubImage(rect)
        same = snapshot.sameAs(image, percent)
        logging.debug('%s same %d' % (path, same))
        return same

def main():
    cr = CookieRunKingdom()
    list = [
        ('wood3.png', (1610, 660, 165, 175), int(1000 - (1000 % 81) - (36 * 2)), (2325, 900)),
        ('jelly3.png', (1610, 660, 165, 175), int(900 - (1000 % 81) - (36 * 2)), (2325, 900)),
        ('sugar3.png', (1610, 660, 165, 175), int(800 - (1000 % 81) - (36 * 2)), (2325, 900)),
        ('biscuit3.png', (1610, 660, 165, 175), int(600 - (1000 % 81) - (36 * 2)), (2325, 900)),
        ('jellyberry3.png', (1610, 660, 165, 175), int(500 - (1000 % 81) - (36 * 2)), (2325, 900)),
        ('milk1.png', (1610, 260, 165, 145), int(81 - (6 * 2)), (2325, 485)),
        ('cottoncandy1.png', (1610, 260, 165, 145), int(81 - (3 * 1)), (2325, 485))
    ]
    stores = [
        ('똑딱 대장간', 60),
        ('설탕용땅 짐가게', 100),
        ('돌웨이크 공작소', 80),
        ('갖 구운 빵집', 50),
        ('챔파이 레스토랑', 50),
        ('토닥토다 도예공방', 60)
    ]
    while True:
        with open('/Users/a201510003/Library/Mobile Documents/com~apple~CloudDocs/Downloads/robot.cfg', 'r') as f:
            robotCfg = f.read()
            robotCfg = robotCfg.strip()
            if robotCfg == 'N':
                logging.debug('robotCfg:%s' % robotCfg)
                sleep(60 * 1)
                continue

        if cr.sameAsImage('expireauth1.png', (910, 665, 735, 50), percent=0.9) or cr.sameAsImage('requestunkownerror.png', (890, 665, 780, 50), percent=0.9):
            cr.kill()
            while cr.ready():
                sleep(3)
            while True:
                # if cr.sameAsImage('touchtostart.png', (210, 925, 255, 185)):
                if cr.sameAsImage('touchtostart.png', (1210, 100, 130, 120)):
                    sleep(20)
                    break
                sleep(2)
            if cr.sameAsImage('downloadpatch.png', (945, 510, 655, 55)):
                cr.touch(1275, 1015)
                sleep(60 * 2)
            cr.touch(1280, 1320)
            while True:
                if cr.sameAsImage('mainpopup.png', (265, 140, 115, 120)):
                    break
                sleep(2)
            sleep(5)
            cr.touch(2485, 80)
            cr.touch(1300, 900)
            cr.touch(1300, 900)
        elif cr.sameAsImage("produceclose.png", (2455, 50, 55, 55), capture=False):
            if cr.sameAsImage('epresso.png', (1610, 260, 165, 145), capture=False) == False and cr.sameAsImage('eventgoods.png', (1610, 260, 165, 140), capture=False) == False:
                cr.touch(835, 680)
                sleep(2)
                capture = False
                if cr.sameAsImage('close.png', (1720, 360, 55, 55), percent=0.9):
                    capture = True
                    cr.touch(1750, 390)
                if cr.sameAsImage('queue3.png', (135, 610, 140, 140), capture=capture) or cr.sameAsImage('queue4.png', (135, 810, 140, 140), capture=False):
                    found = False
                    for i in list:
                        if cr.sameAsImage(i[0], i[1], capture=False):
                            found = True
                            stock1 = cr.stock1(capture=False)
                            if stock1 > -1 and stock1 <= i[2]:
                                cr.touch(i[3][0], i[3][1])
                            break
                    
                    if found == False:
                        for i in range(0, 3): cr.dragUp()
                        storeName = cr.storeName(capture=False)
                        storeInfo = [x for x in stores if x[0] == storeName]
                        goodsLimit = 44
                        if len(storeInfo) > 0:
                            goodsLimit = storeInfo[0][1]

                        capture = True
                        green = None
                        firstItem = True
                        i = 0
                        j = 0
                        while i < 2 and j < 3:
                            if green is not None:
                                green = cr.findGreen(green[1] + 300, capture=capture)
                                firstItem = False
                            else:
                                green = cr.findGreen(capture=capture)
                            capture = False
                            
                            if green is not None:
                                if firstItem:
                                    limit = goodsLimit
                                else:
                                    limit = 44
                                stock2 = cr.stock2(green[1], capture=False)
                                if stock2 > -1 and stock2 <= limit - 8:
                                    cr.touch(2325, green[1])
                                    sleep(2)
                                    if cr.sameAsImage('close.png', (1720, 360, 55, 55), percent=0.9):
                                        cr.touch(1750, 390)
                                    break
                                elif stock2 > -1 and stock2 <= limit - 6:
                                    if cr.sameAsImage('tempbuildtime.png', (1595, green[1] + 37, 225, 50), capture=False):
                                        continue
                                    j += 1
                                    cr.saveSubSnapshot("tempbuildtime.png", (1595, green[1] + 37, 225, 50), capture=False)
                                    cr.touch(green[0], green[1])
                                    sleep(2)
                                    if cr.sameAsImage('close.png', (1720, 360, 55, 55), percent=0.9):
                                        cr.touch(1750, 390)
                                else:
                                    logging.debug('reach maximum production.')
                            else:
                                cr.dragDown()
                                i += 1
                                capture = True
                                green = None
            cr.touch(1350, 700)
    
    # cr.saveSnapshot("test.png")
    # cr.saveSubSnapshot("jellyberry3.png", (1610, 660, 165, 175))
    # cr.saveSubSnapshot('epresso.png', (1610, 260, 165, 145))
    # cr.saveSubSnapshot("sample.png", (630, 65, 615, 90))
    # cr.sameAsImage('eventgoods.png', (1610, 260, 165, 140))
    # img = Image.open("sample.png")
    # image = cv2.imread("sample.png", cv2.IMREAD_GRAYSCALE)
    # blurred = cv2.GaussianBlur(image, (5, 5,), 0)
    # edged = cv2.Canny(blurred, 75, 200)
    # cv2.imwrite("inverted.jpg", edged)
    # d = pytesseract.image_to_data(edged, output_type=pytesseract.Output.DICT, config='--psm 4')
    # print(d)
    # n_boxes = len(d['level'])
    # for i in range(n_boxes):
    #     if d['conf'][i] == '-1':
    #         continue
    #     (x, y, w, h, text, conf) = (d['left'][i], d['top'][i],
    #                                 d['width'][i], d['height'][i],
    #                                 d['text'][i], d['conf'][i])
    #     print((x, y, w, h, text, conf))
    # green = cr.findGreen()
    # print(green)
    # cr.saveSubSnapshot("sample.png", (1739, green[1] - 38, 62, 43))
    # reader = easyocr.Reader(['ko', 'en'])
    # result =  reader.readtext('sample.png')
    # print(result)
    # for i in result:
    #     x = i[0][0][0]
    #     y = i[0][0][1]
    #     txt = i[1]
    #     print("%d %d %s" % (x, y, txt))

if __name__=='__main__':
    main()
