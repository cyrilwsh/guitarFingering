class GlobalVar:
    # cost parameters
    # can be trained
    costSamePosition = 0
    costAlongFinger0 = 0

    costFinger1SameFret   = 5
    costFinger234SameFret = 10

    costFinger1SlideDown  = 3
    costFinger1SlideUp    = 2
    costFinger23SlideDown = 2
    costFinger23SlideUp   = 4
    costFinger4SlideDown  = 5
    costFinger4SlideUp    = 10
    costFingerShiftSlide  = 3 # ori=10, encounter chord change bug

    costBetwFret0andOther = 0

    costLocalWeight = 0.2

    costAcrossMeet = 0.25
    costAcrossOut  = 0.5

    # cost chord parameters
    costChordWeight = 4 # ori=0.5, emphasize Chord
    costChordFinger1 = 1
    costChordFinger1withOther = 1
    costChordLocalWeight = 1
    costChordGlobalWeight = 0.2
    costChordFinger4 = 2
    costChordFinger123 = 1
    costChordFingerWeight = 1
    costChordCrowdWeight = 1


def set_costSamePosition(value):
    GlobalVar.costSamePosition = value
def get_costSamePosition():
    return GlobalVar.costSamePosition

def set_costAlongFinger0(value):
    GlobalVar.costAlongFinger0 = value
def get_costAlongFinger0():
    return GlobalVar.costAlongFinger0

def set_costFinger1SameFret(value):
    GlobalVar.costFinger1SameFret = value
def get_costFinger1SameFret():
    return GlobalVar.costFinger1SameFret

def set_costFinger234SameFret(value):
    GlobalVar.costFinger234SameFret = value
def get_costFinger234SameFret():
    return GlobalVar.costFinger234SameFret

def set_costFinger1SlideDown(value):
    GlobalVar.costFinger1SlideDown = value
def get_costFinger1SlideDown():
    return GlobalVar.costFinger1SlideDown

def set_costFinger1SlideUp(value):
    GlobalVar.costFinger1SlideUp = value
def get_costFinger1SlideUp():
    return GlobalVar.costFinger1SlideUp

def set_costFinger23SlideDown(value):
    GlobalVar.costFinger23SlideDown = value
def get_costFinger23SlideDown():
    return GlobalVar.costFinger23SlideDown

def set_costFinger23SlideUp(value):
    GlobalVar.costFinger23SlideUp = value
def get_costFinger23SlideUp():
    return GlobalVar.costFinger23SlideUp

def set_costFinger4SlideDown(value):
    GlobalVar.costFinger4SlideDown = value
def get_costFinger4SlideDown():
    return GlobalVar.costFinger4SlideDown

def set_costFinger4SlideUp(value):
    GlobalVar.costFinger4SlideUp = value
def get_costFinger4SlideUp():
    return GlobalVar.costFinger4SlideUp

def set_costFingerShiftSlide(value):
    GlobalVar.costFingerShiftSlide = value
def get_costFingerShiftSlide():
    return GlobalVar.costFingerShiftSlide

def set_costBetwFret0andOther(value):
    GlobalVar.costBetwFret0andOther = value
def get_costBetwFret0andOther():
    return GlobalVar.costBetwFret0andOther

def set_costLocalWeight(value):
    GlobalVar.costLocalWeight = value
def get_costLocalWeight():
    return GlobalVar.costLocalWeight

def set_costAcrossMeet(value):
    GlobalVar.costAcrossMeet = value
def get_costAcrossMeet():
    return GlobalVar.costAcrossMeet

def set_costAcrossOut(value):
    GlobalVar.costAcrossOut = value
def get_costAcrossOut():
    return GlobalVar.costAcrossOut

def set_costChordWeight(value):
    GlobalVar.costChordWeight = value
def get_costChordWeight():
    return GlobalVar.costChordWeight

def set_costChordFinger1(value):
    GlobalVar.costChordFinger1 = value
def get_costChordFinger1():
    return GlobalVar.costChordFinger1

def set_costChordFinger1withOther(value):
    GlobalVar.costChordFinger1withOther = value
def get_costChordFinger1withOther():
    return GlobalVar.costChordFinger1withOther

def set_costChordLocalWeight(value):
    GlobalVar.costChordLocalWeight = value
def get_costChordLocalWeight():
    return GlobalVar.costChordLocalWeight

def set_costChordGlobalWeight(value):
    GlobalVar.costChordGlobalWeight = value
def get_costChordGlobalWeight():
    return GlobalVar.costChordGlobalWeight

def set_costChordFinger4(value):
    GlobalVar.costChordFinger4 = value
def get_costChordFinger4():
    return GlobalVar.costChordFinger4

def set_costChordFinger123(value):
    GlobalVar.costChordFinger123 = value
def get_costChordFinger123():
    return GlobalVar.costChordFinger123

def set_costChordFingerWeight(value):
    GlobalVar.costChordFingerWeight = value
def get_costChordFingerWeight():
    return GlobalVar.costChordFingerWeight

def set_costChordCrowdWeight(value):
    GlobalVar.costChordCrowdWeight = value
def get_costChordCrowdWeight():
    return GlobalVar.costChordCrowdWeight
