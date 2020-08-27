import sys, os, random
import runLevel
from panda3d.core import *

loadPrcFileData('Change Window Title','window-title Twobot')
loadPrcFileData('Set Window Icon','icon-filename ui/icon.ico')

props = WindowProperties( )
props.setIconFilename( 'ui/icon.ico' )
base.win.requestProperties( props )

import direct.directbase.DirectStart

from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectGui import *

font = loader.loadFont('ui/Helpimtrappedinafont.ttf')
font.setPixelsPerUnit(200)
font.setPageSize(512,512)
font.setNativeAntialias(True)

# Transitions
from direct.showbase.Transitions import Transitions
transition = Transitions(loader)

# The three nodes, which contain the menus
start = aspect2d.attachNewNode('start')
select = aspect2d.attachNewNode('select')
settings = aspect2d.attachNewNode('settings')

# The node for the top bar menu in runlevel.
topbar = aspect2d.attachNewNode('topbar')

# A function to convert normal rgb into Panda rgb
def rgb(r,g,b,a=1):
    return (r/255.0,g/255.0,b/255.0,a)

def loadStart():
    print('Loading start screen')
    select.detachNode()
    settings.detachNode()
    start.reparentTo(aspect2d)

def loadSelect():
    print('Loading level select')
    start.detachNode()
    select.reparentTo(aspect2d)

def loadSettings():
    start.detachNode()
    settings.reparentTo(aspect2d)

def loadQuit():
    print('Quitting Twobot')
    sys.exit()

# Creates title
def largeText(text,y):
    return OnscreenText(
            text=text,
            font=font,
            scale=0.5,
            fg=(1,1,1,1),
            align=TextNode.ALeft,
            pos=(-1.1,0,y)
        )

# Simple text-only button
def button(text,y,command,x=-1):
    return DirectButton(
        text=text,
        text_font=font,
        text_align=TextNode.ALeft,
        pos=(x,0,y),
        scale=0.2,
        text_fg=(1,1,1,1),
        frameColor=(1,1,1,0),
        command=command,
        clickSound=buttonSound
    )

# Toggle button
def toggleToggleButton(state,obj,text,command):
    obj['text'] = text+[': off',': on'][state]
    command(state)

def toggleButton(text,command,y,x=-1,default=1):
    c = DirectCheckButton(
        text=text+[': off',': on'][default],
        boxImage='ui/empty.jpg',
        boxImageScale=0,
        boxRelief=None,
        text_font=font,
        text_align=TextNode.ALeft,
        pos=(x,0,y),
        scale=0.2,
        text_fg=(1,1,1,1),
        frameColor=(1,1,1,0),
        command=toggleToggleButton,
        indicatorValue=default,
        clickSound=buttonSound,
        boxPlacement='right',
        textMayChange=True
    )
    c['extraArgs'] = [c,text,command]
    return c

# Level Button.
def levelButton(filename,status,height):
    # Generates a button with different backgrounds depending on status.
    # Also starts the level when clicked.
    number = int(filename.split('_')[0])
    name = ' '.join(filename.split('_')[1:]).split('.')[0]
    backgroundColor = [
        rgb(100,255,100,0.5),
        rgb(255,255,255,0.5),
        rgb(0,0,0,0.5)
    ][status] # 0 = completed, 1 = available, 2 = locked
    return DirectButton(
        text=name,
        text_font=font,
        #text_align=TextNode.ALeft,
        pos=(0,0,height-number*0.3),
        frameSize=(-5,5,0.7,-0.3),
        frameColor=backgroundColor,
        scale=0.2,
        relief=6,
        command=startLevel,
        extraArgs=['levels/'+filename],
        suppressMouse=False,
        clickSound=buttonSound
    )

# Image button (for the topbar)
def imageButton(image,command,x,y=0.91):
    b = DirectButton(
        image=image,
        image_scale=0.06,
        pos=(x,0,y),
        scale=1,
        text_fg=(1,1,1,1),
        frameColor=(1,1,1,0),
        command=command,
        clickSound=buttonSound,
        sortOrder=100
    )
    b.setTransparency(1)
    return b

# Creates a background image, obviously
def backgroundImage(name):
    iH=PNMImageHeader()
    iH.readHeader(Filename(name))
    yS=float(iH.getYSize())
    np=OnscreenImage(name,parent=aspect2d)
    np.setScale(Vec3(iH.getXSize(),1,yS)/base.win.getXSize())
    return np

'''Sounds'''
buttonSound = base.loader.loadSfx('sfx/button3.wav')
chimeSound = base.loader.loadSfx('sfx/chime.wav')
chimeSound.setVolume(0.2)

soundtrack = False
def playMusic(name):
    global soundtrack
    if soundtrack:
        soundtrack.stop()
    soundtrack = base.loader.loadSfx(name)
    soundtrack.set_loop(True)
    soundtrack.setVolume(0.2)
    soundtrack.play()
playMusic('sfx/relaxing.mp3')

'''START'''

# Background Image
image = backgroundImage('ui/startScreenDark.png')
image.reparentTo(start)

# Title
title = largeText('twobot',1)
title.reparentTo(start)

# Buttons
startButton = button('start game>',-0.25,loadSelect)
settingsButton = button('settings>',-0.40,loadSettings)
endButton = button('quit>',-0.55,loadQuit)

startButton.reparentTo(start)
settingsButton.reparentTo(start)
endButton.reparentTo(start)

'''RUNLEVEL'''

# Grey DirectFrame that appears when paused. Used because the Transitions
# class really doesn't want to cooperate with me for this one.

pauseBlackOut = DirectFrame(
    frameSize = (-300,300,-300,300),
    frameColor = (0,0,0,0.6)
)
pauseBlackOut.detachNode()

def togglePause():
    runLevel.pause = not(runLevel.pause)
    if runLevel.pause:
        pauseBlackOut.reparentTo(topbar)
    else:
        pauseBlackOut.detachNode()

def reset():
    runLevel.reset()
    pauseBlackOut.detachNode()

imageButton('ui/restart.png',reset,x=0).reparentTo(topbar)
imageButton('ui/back.png',runLevel.endLevel,x=-0.25).reparentTo(topbar)
imageButton('ui/pause.png',togglePause,x=0.25).reparentTo(topbar)

def detectWin(task):
    # Detects when the "win" variable is True, plays a darken animation and calls cleanupLevel.
    if runLevel.win:
        print('Level complete')
        transition.fadeOut(t=1)
        chimeSound.play()
        taskMgr.doMethodLater(1,cleanupLevel,'cleanupLevel')
        return
    if runLevel.end:
        print('Level ended')
        cleanupLevel()
        return
    return task.cont

def cleanupLevel(task=None):
    # Clears the level and loads the select screen
    # The unused "task" variable is because this function may be fired by taskMgr.
    transition.noFade()
    runLevel.clearLevel()
    playMusic('sfx/relaxing.mp3')
    topbar.detachNode()
    loadSelect()

def startLevel(name):
    print('Starting level',name)
    select.detachNode()
    runLevel.level = runLevel.makeLevel(name)
    runLevel.win = False
    runLevel.end = False
    runLevel.headingNode.setH(45)
    runLevel.pitchNode.setP(50)
    taskMgr.add(runLevel.run,'run')
    taskMgr.add(detectWin,'detectWin')
    topbar.reparentTo(aspect2d)
    playMusic('sfx/slowmotion.mp3')

#base.accept('r',reset)
#base.accept('x',runLevel.endLevel)

'''SELECT'''

# Get all available level names
levelFileNames = os.listdir('levels')

# Background Image
image = backgroundImage('ui/levelSelectScreen.png')
image.reparentTo(select)

# Back button
backButton = button('<back',0.8,loadStart,x=-1.3)
backButton.reparentTo(select)

# Level-frame
totalHeight = len(levelFileNames)*0.3
levelframe = DirectScrolledFrame(
    canvasSize = (-1.2,1.2,-0.2,totalHeight),
    frameSize = (-1.2,1.2,-0.2,1.5),
    frameColor = (0,0,0,0.1),
    scrollBarWidth = 0
)

levelframe.setPos(0,0,-0.75)
levelframe.reparentTo(select)

# Manually scrolls the frame by movements of the scroll wheel.
def scroll(amount):
    levelframe.verticalScroll['value'] += amount

base.accept('wheel_up',scroll,[-0.2])
base.accept('wheel_down',scroll,[0.2])

# Levels
for i in levelFileNames:
    b = levelButton(i,0,totalHeight)
    b.reparentTo(levelframe.getCanvas())

''' SETTINGS '''
def toggleSound(state):
    if state:
        base.enableAllAudio()
    else:
        base.disableAllAudio()

def toggleShadows(state):
    if state:
        runLevel.mainLight.node().setShadowCaster(True,4096,4096)
    else:
        runLevel.mainLight.node().setShadowCaster(False)

def toggleDebug(state):
    if state:
        runLevel.debugNP.show()
    else:
        runLevel.debugNP.hide()

# Background Image
image = backgroundImage('ui/rockGreyBackground.png')
image.reparentTo(settings)

# Back button
backButton = button('<back',0.8,loadStart,x=-1.3)
backButton.reparentTo(settings)

largeText('settings',1).reparentTo(settings)

toggleButton('sound',toggleSound,-0.25).reparentTo(settings)
toggleButton('shadows',toggleShadows,-0.40).reparentTo(settings)
toggleButton('debug mode',toggleDebug,-0.55,default=0).reparentTo(settings)

start.detachNode()
select.detachNode()
settings.detachNode()

if __name__ == '__main__':
    loadStart()
    base.run()