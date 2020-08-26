import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.core import *

# Add some text
bk_text = "This is my Demo"
textObject = OnscreenText(text=bk_text, pos=(0.95,-0.95), scale=0.07,
                          fg=(1, 0.5, 0.5, 1), align=TextNode.ACenter,
                          mayChange=1)

# Callback function to set  text
def setText(status):
    if status:
        bk_text = "Checkbox Selected"
    else:
        bk_text = "Checkbox Not Selected"
    textObject.setText(bk_text)

# Add button
b = DirectCheckButton(text = "CheckButton" ,scale=.05,command=setText)

# Run the tutorial
base.run()