'''Initialization'''

# Imports. I'm importing * because I'm too lazy to go through
# and only import what I need.

import random, time, os, copy
from panda3d.core import *
from panda3d.bullet import *
from direct.directnotify.Notifier import Notifier

#loadPrcFileData('Change Collision Filtering To Groups','bullet-filter-algorithm groups-mask')
loadPrcFileData('Change Window Title','window-title Twobot')
#loadPrcFileData('Disable Cache','model-cache-dir')
 
import direct.directbase.DirectStart

from direct.particles.ParticleEffect import ParticleEffect

# Disable warning messages
n = Notifier('notifier')
n.setWarning(bool=False)

# Turns debug mode on to make sure I'm not doing something weird.
debugNode = BulletDebugNode('Debug')
debugNode.showWireframe(True)
debugNode.showConstraints(True)
debugNode.showBoundingBoxes(False)
debugNode.showNormals(False)
debugNP = render.attachNewNode(debugNode)
#debugNP.show()

# A function to convert normal rgb into Panda rgb
def rgb(r,g,b,a=1):
    return (r/255.0,g/255.0,b/255.0,a)

# Get all available level names
def getLevelNames():
    return os.listdir('levels')

availableLevels = getLevelNames()
levelCtr = 0

# The sky
base.setBackgroundColor(1,1,1)#rgb(211, 230, 235))

# Disable default mouse controls.
base.disableMouse()

# Enable particles
base.enableParticles()

render.setAntialias(AntialiasAttrib.MAuto)

# Camera Nodes
headingNode = render.attachNewNode('headingNode')
headingNode.setH(45)
pitchNode = headingNode.attachNewNode('pitchNode')
pitchNode.setP(10)
camera.reparentTo(pitchNode)
camera.setPos(0,0,20)
camera.lookAt(headingNode)

# Center node for mouse orbit
centerNode = render.attachNewNode('centerNode')
centerNode.setPos(0,0,0)

'''Physics'''

# Initialize the gravity vector
gravityVector = Vec3(0,0,-9.8)

# Make the Bullet Physics World
world = BulletWorld()
world.setGravity(gravityVector)
world.setDebugNode(debugNP.node())

'''Lighting'''
'''# Ambient
alight = AmbientLight('alight')
alight.setColor((0.4,0.4,0.4,1))
np = render.attachNewNode(alight)
render.setLight(np)

mainLight = render.attachNewNode(Spotlight("Spot"))
mainLight.node().setColor(rgb(255,255,255))
mainLight.node().setScene(render)
mainLight.node().setShadowCaster(True,4096,4096)

mainLight.node().getLens().setFov(40)
mainLight.setPos(0,0,40)
mainLight.setHpr(-45,-90,0)
mainLight.node().getLens().setNearFar(10, 100)
render.setLight(mainLight)'''

# Ambient
alight = AmbientLight('alight')
alight.setColor((0.5,0.5,0.5,1))
np = render.attachNewNode(alight)
render.setLight(np)

mainLight = render.attachNewNode(Spotlight("Spot"))
mainLight.node().setColor(rgb(255,200,100))
mainLight.node().setScene(render)
mainLight.node().setShadowCaster(True,4096,4096)
#mainLight.node().showFrustum()
mainLight.node().getLens().setFov(40)
mainLight.setPos(0,0,40)
mainLight.setHpr(-45,-90,0)
mainLight.node().getLens().setNearFar(10, 100)
render.setLight(mainLight)

# Enable the shader generator for the receiving nodes
render.setShaderAuto()

#mainLight.node().showFrustum()

'''Models'''
blockModel = loader.loadModel('models/block/block2.dae')
#blockModel.setColorScale(rgb(39, 40, 34, 0.3))
blockModel.setColorScale(rgb(80,70,65))
grassModel = loader.loadModel('models/block/grass2.dae')
rockModel = loader.loadModel('models/rocks/rock.dae')

'''Classes'''
# Static object
class static():
    def __init__(self,x,y,z,model):
        # Coordinates, obviously
        self.x = x
        self.y = y
        self.z = z

        # Setup physics
        shape = BulletBoxShape(Vec3(0.5,0.5,0.5))
        self.node = BulletRigidBodyNode('block')
        self.node.addShape(shape)
        self.nodePath = render.attachNewNode(self.node)
        world.attachRigidBody(self.node)

        self.nodePath.setPos(self.x,self.y,self.z)
        self.nodePath.setCollideMask(BitMask32.bit(0))
        
        # Set the model
        self.model = model
        self.model.setScale(0.5,0.5,0.5)
        n = random.random()*0.3+0.7
        self.nodePath.setColorScale(n)
        self.model.instanceTo(self.nodePath)
        self.model.setHpr(0,90,0)

class block(static):
    def __init__(self,x,y,z):
        super().__init__(x,y,z,blockModel)
        self.type = 'block'

class grass(static):
    def __init__(self,x,y,z):
        super().__init__(x,y,z,grassModel)
        self.type = 'block'

class rock(static):
    def __init__(self,x,y,z):
        super().__init__(x,y,z,rockModel)
        self.type = 'rock'  

class tree(static):
    def __init__(self,x,y,z):
        super().__init__(x,y,z,'models/tree3.dae')
        self.type = 'tree'
        self.model.setScale(0.4,0.5,0.4)
        self.model.setPos(0.1,-0.1,0.25)

class stair():
    def __init__(self,x,y,z,h):
        self.type = 'stair'

        #topStair = BulletBoxShape(Vec3(0.5,0.25,0.5))
        #bottomStair = BulletBoxShape(Vec3(0.5,0.5,0.25))

        bottomStep = BulletBoxShape(Vec3(0.5,0.33/2,0.33/2))
        middleStep = BulletBoxShape(Vec3(0.5,0.33/2,0.66/2))
        topStep    = BulletBoxShape(Vec3(0.5,0.33/2,0.5))

        self.node = BulletRigidBodyNode('stair')
        #self.node.addShape(topStair, TransformState.makePos(Point3(0, 0.25, 0)))
        #self.node.addShape(bottomStair, TransformState.makePos(Point3(0, 0, -0.25)))
        self.node.addShape(bottomStep, TransformState.makePos(Point3(0,-0.33,-0.66/2)))
        self.node.addShape(middleStep, TransformState.makePos(Point3(0,0,-0.33/2)))
        self.node.addShape(   topStep, TransformState.makePos(Point3(0,0.33,0)))

        self.nodePath = render.attachNewNode(self.node)
        world.attach(self.node)

        self.nodePath.setPos(x,y,z)
        self.nodePath.setH(h)

        self.model = loader.loadModel('models/stairs/stair2.dae')
        self.model.setHpr(-90,90,0)
        self.model.setScale(0.5)
        self.model.reparentTo(self.nodePath)

#Ball
class ball():
    def __init__(self,x,y,z):
        self.x = x
        self.y = y
        self.z = z

        # Setup physics
        shape = BulletSphereShape(0.5)
        self.node = BulletRigidBodyNode('ball')
        self.node.addShape(shape)
        self.node.setMass(2.0)
        self.nodePath = render.attachNewNode(self.node)
        world.attachRigidBody(self.node)

        self.nodePath.setPos(self.x,self.y,self.z)
        self.nodePath.setCollideMask(BitMask32.bit(0))

        # Enable shadows
        ##self.nodePath.setLight(dynamicLight)
        #self.nodePath.setShaderAuto()
        
        # Set the model
        self.model = loader.loadModel('models/ball.dae')
        self.model.setScale(0.5,0.5,0.5)
        self.model.reparentTo(self.nodePath)
        self.model.setHpr(0,90,0)
        
        self.type = 'ball'
    
    def reset(self):
        self.nodePath.setPos((self.x,self.y,self.z))
        self.nodePath.setHpr(0,0,0)
        self.node.clearForces()
        self.node.angular_velocity = Vec3(0,0,0)
        self.node.linear_velocity = Vec3(0,0,0)
        

#Dynamic Object
class box():
    def __init__(self,positions):
        self.type = 'box'

        # Get the center of mass

        self.x = sum([i[0] for i in positions])/len(positions)
        self.y = sum([i[1] for i in positions])/len(positions)
        self.z = sum([i[2] for i in positions])/len(positions)

        # Setup physics
        
        self.node = BulletRigidBodyNode('box')
        self.node.setMass(20.0)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setCollideMask(BitMask32.bit(0))
        self.nodePath.setPos((self.x,self.y,self.z))

        # Load the box model
        blockModel = loader.loadModel('models/box.dae')
        blockModel.setHpr(0,90,0)
        blockModel.setScale(0.5,0.5,0.5)

        # Enable shadows
        ##self.nodePath.setLight(dynamicLight)
        #self.nodePath.setShaderAuto()

        shape = BulletBoxShape(Vec3(0.49,0.49,0.49))

        # Now, go through all the positions and add physics shapes and models
        #print('box positions: '+str(positions))
        for unit in positions:
            # Position the new shape relative to the center of mass
            transform = TransformState.makePos(Point3(unit[0]-self.x,unit[1]-self.y,unit[2]-self.z))
            # Add the shape to the node
            self.node.addShape(shape,transform)
            # Add the model to the nodePath
            modelNode = self.nodePath.attachNewNode('modelNode')
            modelNode.setPos(unit[0]-self.x,unit[1]-self.y,unit[2]-self.z)
            blockModel.instanceTo(modelNode)
        world.attachRigidBody(self.node)

    def reset(self):
        self.nodePath.setPos((self.x,self.y,self.z))
        self.nodePath.setHpr(0,0,0)
        self.node.clearForces()
        self.node.angular_velocity = Vec3(0,0,0)
        self.node.linear_velocity = Vec3(0,0,0)

# Vents
class vent():
    def __init__(self,x,y,z):
        self.type = 'vent'

        # Physics - GhostNode
        shape = BulletCylinderShape(0.1,3,ZUp)
        self.node = BulletGhostNode()
        self.node.addShape(shape)
        world.attachGhost(self.node)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setCollideMask(BitMask32.bit(0))

        self.nodePath.setPos(Vec3(x,y,z))
        
        # Base model
        self.model = loader.loadModel('models/vent.dae')
        self.model.setHpr(0,90,0)
        self.model.setScale(0.5)
        self.model.reparentTo(self.nodePath)

        # Particle system
        self.particles = ParticleEffect()
        self.particles.loadConfig('models/vent2.ptf')
        self.particles.start(parent=self.nodePath)

# EndPlate

deletedPlayers = []

class endPlate():
    def __init__(self,x,y,z):
        self.type = 'endPlate'

        # Physics - GhostNode
        shape = BulletCylinderShape(0.3,0.5,ZUp)
        self.node = BulletGhostNode()
        self.node.addShape(shape)
        world.attachGhost(self.node)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setPos(x,y,z)
        
        self.model = loader.loadModel('models/endPlate/endPlate.dae')
        self.model.reparentTo(self.nodePath)
        self.model.setHpr(0,90,0)
        self.model.setScale(0.5)

        # Particle system
        self.particles = ParticleEffect()
        self.particles.loadConfig('models/endPlate/endPlate.ptf')
        self.particles.start(parent=self.nodePath)

        self.chime = base.loader.loadSfx('sfx/electricChime.wav')
        self.chime.setVolume(0.3)

    def checkWin(self):
        global deletedPlayers
        overlaps = self.node.getOverlappingNodes()
        allGood = True
        for obj in level:
            if obj.type == 'player':
                if obj.node in overlaps and abs(obj.nodePath.getX()-self.nodePath.getX()) <= 0.3 and abs(obj.nodePath.getY()-self.nodePath.getY()) <= 0.3:
                    obj.delete()
                    deletedPlayers.append(obj)
                    self.chime.play()
                elif obj not in deletedPlayers:
                    allGood = False
        return allGood

# Mines
class mine():
    def __init__(self,x,y,z):
        self.type = 'mine'

        # Physics - GhostNode
        shape = BulletCylinderShape(1,1,ZUp)
        self.ghostnode = BulletGhostNode()
        self.ghostnode.addShape(shape)
        self.node = BulletRigidBodyNode()
        self.node.addShape(shape)
        world.attach(self.ghostnode)
        world.attach(self.node)
        self.nodePath = render.attachNewNode(self.ghostnode)
        #self.rigidNodePath = self.nodePath.attachNewNode(self.node)
        self.nodePath.setCollideMask(BitMask32.bit(0))

        self.nodePath.setPos(Vec3(x,y,z))
        
        # Base model
        self.model = loader.loadModel('models/mine4.dae')
        self.model.setHpr(0,90,0)
        self.model.setScale(0.5)
        self.model.reparentTo(self.nodePath)

        self.frame = 0
        self.explodeFrame = -1

    def explode(self):
        #global mainPlayer
        #print(self.frame)
        self.frame += 1
        if self.explodeFrame > self.frame or self.explodeFrame == -1:
            for node in self.ghostnode.getOverlappingNodes():
                if node.name == 'player':
                    #if abs(mainPlayer.nodePath.getX()-self.nodePath.getX()) < 2 and abs(mainPlayer.nodePath.getY()-self.nodePath.getY()) < 2:
                    #self.explodeFrame = self.frame
                    reset()
        else:
            self.model.detachNode()
            #world.removeRigidBody(self.node)
            #self.rigidNodePath.detachNode()
            #print(self.explodeFrame,self.frame)

    def reset(self):
        self.frame = 0
        self.model.reparentTo(self.nodePath)

# Point-lights
class light():
    def __init__(self,x,y,z):
        self.light = render.attachNewNode(PointLight('light'))
        self.type = 'light'
        self.light.setPos(x,y,z)
        self.light.node().setColor(rgb(230,230,230,0.7))
        render.setLight(self.light)
    def delete(self):
        render.clearLight(self.light)
        self.light.detachNode()

# The Freaking Player
class player():
    def __init__(self,x,y,z,h=0,short=True):
        # Coordinates, obviously
        self.x = x
        self.y = y
        if short:
            self.z = z
        else:
            self.z = z+0.5
        self.sh = h # Starting heading
        self.h = h # Current heading

        self.type = 'player'

        # Setup physics

        if short:
            shape = BulletSphereShape(0.5)
        else:
            shape = BulletCapsuleShape(0.5,1,ZUp)

        self.node = BulletRigidBodyNode('player')
        self.node.addShape(shape)
        self.node.setMass(3.0)
        self.node.deactivation_enabled = False
        self.nodePath = render.attachNewNode(self.node)
        world.attach(self.node)

        # Position, duh
        self.pos = Vec3(self.x,self.y,self.z)
        self.nodePath.setPos(self.pos)
        self.nodePath.setH(self.sh)
        
        # Load the model
        if short:
            self.model = loader.loadModel('models/bots/levi.dae')
        else:
            self.model = loader.loadModel('models/bots/roller3.dae')
            self.model.setZ(-0.5)

        self.model.setHpr(0,90,0)
        self.model.setScale(0.5,0.5,0.5)
        self.model.reparentTo(self.nodePath)
        
        ghostShape = BulletSphereShape(0.05)

        self.frontNode = BulletGhostNode()
        self.frontNode.addShape(ghostShape)
        world.attachGhost(self.frontNode)
        self.nodePath.attachNewNode(self.frontNode)
        NodePath(self.frontNode).setY(-0.55)

        self.backNode = BulletGhostNode()
        self.backNode.addShape(ghostShape)
        world.attach(self.backNode)
        self.nodePath.attachNewNode(self.backNode)
        NodePath(self.backNode).setY(0.55)

        if not(short):
            NodePath(self.frontNode).setZ(-0.5)
            NodePath(self.backNode).setZ(-0.5)

        #self.camNode = render.attachNewNode('camNode')
        self.node.setGravity(Vec3(0,0,-30))
    
    def setStatic(self):
        # Set boxes to static when walking on them
        for node in self.ghostNode.getOverlappingNodes():
            if node.name in ['box','ball']:
                node.setMass(0)

    def reset(self):
        self.nodePath.reparentTo(render)
        self.model.reparentTo(self.nodePath)
        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.sh,0,0)
        self.h = self.sh
        self.node.setLinearVelocity(Vec3(0,0,0))
        world.attach(self.node)

    def delete(self):
        self.model.detachNode()
        world.remove(self.node)
        self.nodePath.detachNode()

#TODO FIX THIS
def buildBox(pos,pastPositions,splitLevelString):
    if pos in pastPositions:
        return False
    pastPositions.append(pos)
    boxPositions = []
    for rz in [-1,0,1]:
        if rz+pos[2] >= 0 and rz+pos[2] < len(splitLevelString):
            for ry in [-1,0,1]:
                if ry+pos[1] >= 0 and ry+pos[1] < len(splitLevelString[rz+pos[2]]):
                    for rx in [-1,0,1]:
                        if rx+pos[0] >= 0 and rx+pos[0] < len(splitLevelString[rz+pos[2]][ry+pos[1]]):
                            if [rx,ry,rz] != [0,0,0]:
                                if splitLevelString[rz+pos[2]][ry+pos[1]][rx+pos[0]] == 'b':
                                    npos = [rx+pos[0],ry+pos[1],rz+pos[2]]
                                    if not npos in pastPositions:
                                        #print(pastPositions)
                                        #print(npos,str(npos in pastPositions))
                                        rec = buildBox(npos,pastPositions,splitLevelString)
                                        boxPositions+=[i for i in rec]
                                        #pastPositions=rec[1]
    boxPositions.append(pos)
    pastPositions+=boxPositions
    #print(boxPositions)
    return boxPositions

def reset():
    global level, deletedPlayers, pause
    pause = False
    deletedPlayers = []
    for i in level:
        if i.type in ['player','box','mine','turret','ball']:
            i.reset()

def makeLevel(name):
    level = []
    with open(name,'r') as levelString:
        splitLevelString = list(map(lambda i:i.split('\n'),levelString.read().split('---\n')))
    totalZ = 0
    totalY = 0
    totalX = 0
    totalBlocks = 0
    pastPositions = []
    for z in range(len(splitLevelString)):
        for y in range(len(splitLevelString[z])):
            for tx in range(len(splitLevelString[z][y])):
                x = -tx
                char = splitLevelString[z][y][tx]

                item = False

                if char != ' ':

                    totalZ += z
                    totalY += y
                    totalX += x
                    totalBlocks += 1

                    if   char == '#': item = block(x,y,z)
                    elif char == '.': item = grass(x,y,z)
                    elif char == '^': item = rock(x,y,z)
                    
                    elif char == 'w': item = player(x,y,z,h=0)
                    elif char == 's': item = player(x,y,z,h=180)
                    elif char == 'a': item = player(x,y,z,h=90)
                    elif char == 'd': item = player(x,y,z,h=-90)
                    
                    elif char == '|': item = player(x,y,z,h=0,short=False)
                    elif char == '/': item = player(x,y,z,h=180,short=False)
                    elif char == '-': item = player(x,y,z,h=90,short=False)
                    elif char == '_': item = player(x,y,z,h=-90,short=False)

                    elif char == 'i': item = stair(x,y,z,h=0)
                    elif char == 'k': item = stair(x,y,z,h=180)
                    elif char == 'j': item = stair(x,y,z,h=-90)
                    elif char == 'l': item = stair(x,y,z,h=90)

                    elif char == 'v': item = vent(x,y,z)
                    
                    elif char == 'b':
                        units = buildBox([tx,y,z],pastPositions,splitLevelString)
                        if units:
                            pastPositions += copy.deepcopy(units)
                            for i in units:
                                i[0] *= -1
                            item = box(units)
                    elif char == 'o': item = ball(x,y,z)
                    
                    elif char == 'm': item = mine(x,y,z)
                    elif char == 't': print('Turret has not been implemented yet')

                    elif char == '*': item = light(x,y,z)

                    elif char == 'x': item = endPlate(x,y,z)

                if item: level.append(item)

    del pastPositions
    headingNode.setPos((totalX/totalBlocks,totalY/totalBlocks,totalZ/totalBlocks))
    camera.lookAt(headingNode)
    return level

def camControl():
    k = base.mouseWatcherNode.isButtonDown
    l = KeyboardButton
    if k(l.up()):
        pitchNode.setHpr(pitchNode,Vec3(0,-3,0))
    if k(l.down()):
        pitchNode.setHpr(pitchNode,Vec3(0,3,0))
    if k(l.left()):
        headingNode.setHpr(headingNode,Vec3(-3,0,0))
    if k(l.right()):
        headingNode.setHpr(headingNode,Vec3(3,0,0))
    if k(KeyboardButton.asciiKey('n')): #Zoom out
        camera.setPos(camera,Vec3(0,-0.5,0))
    if k(KeyboardButton.asciiKey('m')): #Zoom in
        camera.setPos(camera,Vec3(0,0.5,0))

def isThingTouching(name,ghostnode):
    for i in ghostnode.getOverlappingNodes():
        if i.name == name:
            x,y,_ = NodePath(i).getPos()
            gx,gy,_ = NodePath(ghostnode).getPos(render)
            #print(x,y,gx,gy)
            if abs(x-gx) < 0.55 and abs(y-gy) < 0.55:
                return True
    return False

def isPressed(key):
    return base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(key))

def keyboardControl():
    speed = Vec3(0, 0, 0)
    omega = 0.0

    v = 0.05
    forward = 1

    if isPressed('w'):
        speed.setY(-v)
    if isPressed('s'):
        speed.setY(v)
        forward = 0

    for i in level:
        if i.type == 'player':
            #i.node.setLinearMovement(speed, True)
            i.node.setAngularVelocity(Vec3(0,0,0))
            i.nodePath.setP(0)
            i.nodePath.setR(0)
            zVel = i.node.getLinearVelocity()[2]
            i.node.setLinearVelocity(Vec3(0,0,zVel))
            # TODO get the ghostNodes to stop firing incorrectly
            if not((forward and isThingTouching('block',i.frontNode)) or (not(forward) and isThingTouching('block',i.backNode))):
                #print([n.name for n in i.frontNode.getOverlappingNodes()])
                #speed.setY(speed.getY()/2)
                i.nodePath.setPos(i.nodePath,speed)

def turnPlayer(deg):
    global pause
    if not(pause):
        for j in level:
            if j.type == 'player':
                #print(j.h)
                i = j.nodePath.hprInterval(0.2,Vec3(j.h+deg,0,0),startHpr=Vec3(j.h,0,0))
                j.h += deg
                if j.h >= 180: j.h -= 360
                if j.h < -180: j.h += 360
                i.start()

base.accept('d',turnPlayer,[-90])
base.accept('a',turnPlayer,[90])

def applyVentForce():
    global level
    for i in level:
        if i.type == 'vent':
            for node in i.node.getOverlappingNodes():
                if node.name == 'box' or node.name == 'ball' or node.name == 'player':
                    parent = NodePath(node)
                    zDist = (parent.getZ()-i.nodePath.getZ())*50
                    node.applyCentralForce(Vec3(0,0,120-zDist))

def setStatic():
    for obj in level:
        if obj.type in ['box','ball'] and obj.node.getMass() == 0:
            obj.node.setMass(2)
    for i in level:
        if i.type == 'player' or i.type == 'ghost':
            i.setStatic()

def mineExplode():
    for i in level:
        if i.type == 'mine':
            i.explode()

def checkWin():
    for i in level:
        if i.type == 'endPlate':
            if i.checkWin(): return True
    return False

def physics():
    dt = globalClock.getDt()
    world.doPhysics(dt, 10, 1.0/180.0)

win = False
end = False
pause = False

def run(task):
    global level, win, end, pause
    if not (pause):
        camControl()
        keyboardControl()
        applyVentForce()
        physics()
        mineExplode()
        #setStatic()
        if end: return
        if checkWin():
            win = True
            return
    return task.cont

def clearLevel():
    global level
    for i in level:
        if i.type == 'light':
            i.delete()
        else:
            if i.type == 'player':
                world.remove(i.frontNode)
                world.remove(i.backNode)
            world.remove(i.node)
            i.nodePath.removeNode()
    level = [] 

def nextLevel():
    global level, levelCtr
    clearLevel()
    levelCtr += 1
    level = makeLevel('levels\\'+availableLevels[levelCtr])

def endLevel():
    global end
    end = True

if __name__ == '__main__':
    level = makeLevel('levels\\'+availableLevels[levelCtr])    
    base.accept('c',nextLevel)
    taskMgr.add(run,'run')
    #taskMgr.add(bakeShadows,'bakeShadows')
    base.run()