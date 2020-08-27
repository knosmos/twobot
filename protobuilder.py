'''Initialization'''

# Imports. I'm importing * because I'm too lazy to go through
# and only import what I need.

import random, time, os, sys, copy
from panda3d.core import *
from panda3d.bullet import *
from direct.directnotify.Notifier import Notifier

#loadPrcFileData('Change Collision Filtering To Groups','bullet-filter-algorithm groups-mask')
loadPrcFileData('Change Window Title','window-title Yochin Is Not Annoying')
#loadPrcFileData('Disable Cache','model-cache-dir')

import direct.directbase.DirectStart

from direct.particles.ParticleEffect import ParticleEffect

# Disable warning messages
n = Notifier('notifier')
n.setWarning(bool=False)

# A function to convert normal rgb into Panda rgb
def rgb(r,g,b,a=1):
    return (r/255.0,g/255.0,b/255.0,a)

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
camera.reparentTo(pitchNode)
camera.setPos(0,5,10)
camera.lookAt(headingNode)

# Center node for mouse orbit
centerNode = render.attachNewNode('centerNode')
centerNode.setPos(0,0,0)

'''Physics'''

# Initialize the gravity vector
gravityVector = Vec3(0,0,-9)

# Make the Bullet Physics World
world = BulletWorld()
world.setGravity(gravityVector)

'''Lighting'''
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

'''Models'''
blockModel = loader.loadModel('models/block/block.dae')
blockModel.setColorScale(rgb(39, 40, 34, 0.3))
grassModel = loader.loadModel('models/block/grass2.dae')
rockModel = loader.loadModel('models/rocks/rock.dae')

baseplate = loader.loadModel('models/baseplate.dae')
baseplate.reparentTo(render)
baseplate.setP(90)
baseplate.setZ(-0.5)

alight = AmbientLight('blight')
alight.setColor((0.45,0.45,0.45,1))
np = render.attachNewNode(alight)
baseplate.setLight(np)

'''Sounds'''
soundtrack = base.loader.loadSfx('sfx/streamflow.ogg')
soundtrack.set_loop(True)
soundtrack.setVolume(0.2)
soundtrack.play()
#print(soundtrack.getTime())

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

        topStair = BulletBoxShape(Vec3(0.5,0.25,0.4))
        bottomStair = BulletBoxShape(Vec3(0.5,0.5,0.20))

        self.node = BulletRigidBodyNode('stair')
        self.node.addShape(topStair, TransformState.makePos(Point3(0, 0.25, -0.1)))
        self.node.addShape(bottomStair, TransformState.makePos(Point3(0, 0, -0.30)))
        self.nodePath = render.attachNewNode(self.node)
        world.attach(self.node)

        self.nodePath.setPos(x,y,z)
        self.nodePath.setH(h)

        self.model = loader.loadModel('models/stair.dae')
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
        self.node.setMass(10.0)
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
        shape = BulletCylinderShape(0.1,1,ZUp)
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
    
    def checkWin(self):
        global deletedPlayers
        overlaps = self.node.getOverlappingNodes()
        allGood = True
        for obj in level:
            if obj.type == 'player':
                if obj.node in overlaps:
                    obj.delete()
                    deletedPlayers.append(obj)
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
        print(self.explodeFrame)
        self.model.reparentTo(self.nodePath)

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
        self.h = h

        self.type = 'player'

        # Setup physics

        if short:
            shape = BulletSphereShape(0.5)
        else:
            shape = BulletCapsuleShape(0.5,1,ZUp)

        self.node = BulletRigidBodyNode('player')
        self.node.addShape(shape)
        self.node.setMass(3.0)
        self.nodePath = render.attachNewNode(self.node)
        world.attach(self.node)

        # Position, duh
        self.pos = Vec3(self.x,self.y,self.z)
        self.nodePath.setPos(self.pos)
        self.nodePath.setH(self.h)
        
        # Load the model
        if short:
            self.model = loader.loadModel('models/bots/levi.dae')
        else:
            self.model = loader.loadModel('models/bots/roller3.dae')
            self.model.setZ(-0.5)

        self.model.setHpr(0,90,0)
        self.model.setScale(0.5,0.5,0.5)
        self.model.reparentTo(self.nodePath)

        ghostShape = BulletSphereShape(0.1)
        self.ghostNode = BulletGhostNode()
        self.ghostNode.addShape(ghostShape)
        world.attach(self.ghostNode)
        self.ghostNodePath = self.nodePath.attachNewNode(self.ghostNode)
        self.ghostNodePath.setZ(-1)

        self.camNode = render.attachNewNode('camNode')
    
    def setStatic(self):
        # Set boxes to static when walking on them
        for node in self.ghostNode.getOverlappingNodes():
            if node.name in ['box','ball']:
                node.setMass(0)

    def reset(self):
        self.nodePath.reparentTo(render)
        self.model.reparentTo(self.nodePath)
        self.nodePath.setPos(self.pos)
        self.nodePath.setHpr(self.h,0,0)
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
    global level
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
                            #print(units)
                            pastPositions += copy.deepcopy(units)
                            for i in units:
                                i[0] *= -1
                            item = box(units)
                    elif char == 'o': item = ball(x,y,z)
                    
                    elif char == 'm': item = mine(x,y,z)
                    elif char == 't': print('Turret has not been implemented yet')

                    elif char == 'x': item = endPlate(x,y,z)

                if item: level.append(item)
    #print(pastPositions)
    del pastPositions
    headingNode.setPos((totalX/totalBlocks,totalY/totalBlocks,totalZ/totalBlocks))
    camera.lookAt(headingNode)
    return level

def camControl():
    k = base.mouseWatcherNode.isButtonDown
    l = KeyboardButton
    if k(l.up()):
        pitchNode.setHpr(pitchNode,Vec3(0,3,0))
    if k(l.down()):
        pitchNode.setHpr(pitchNode,Vec3(0,-3,0))
    if k(l.left()):
        headingNode.setHpr(headingNode,Vec3(-3,0,0))
    if k(l.right()):
        headingNode.setHpr(headingNode,Vec3(3,0,0))
    if k(KeyboardButton.asciiKey('n')): #Zoom out
        camera.setPos(camera,Vec3(0,-0.5,0))
    if k(KeyboardButton.asciiKey('m')): #Zoom in
        camera.setPos(camera,Vec3(0,0.5,0))

def isPressed(key):
    return base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey(key))

def keyboardControl():
    speed = Vec3(0, 0, 0)
    omega = 0.0

    v = 0.05

    if isPressed('w'): speed.setY(-v)
    if isPressed('s'): speed.setY( v)

    for i in level:
        if i.type == 'player':
            #i.node.setLinearMovement(speed, True)
            i.nodePath.setPos(i.nodePath,speed)
            i.node.setAngularVelocity(Vec3(0,0,0))
            i.nodePath.setP(0)
            i.nodePath.setR(0)
            zVel = i.node.getLinearVelocity()[2]
            i.node.setLinearVelocity(Vec3(0,0,zVel))

def turnPlayer(deg):
    for j in level:
        if j.type == 'player':
            h = j.nodePath.getHpr()
            i = j.nodePath.hprInterval(0.2,(h[0]+deg,h[1],h[2]))
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
                    print(zDist)
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

def run(task):
    global level, levelCtr
    camControl()
    keyboardControl()
    applyVentForce()
    physics()
    mineExplode()
    #setStatic()
    checkWin()
    return task.cont

def refresh():
    global level
    for i in level:
        world.remove(i.node)
        i.nodePath.removeNode()
    level = []
    level = makeLevel('levels\\'+sys.argv[1])

level = makeLevel('levels\\'+sys.argv[1])

base.accept('r',reset)
base.accept('c',refresh)

taskMgr.add(run,'run')
#taskMgr.add(bakeShadows,'bakeShadows')
base.run()