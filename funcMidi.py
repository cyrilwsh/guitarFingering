import matplotlib.pyplot as plt
import numpy as np
from mido import MidiFile
""" Copy right for mido
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from fpdf import FPDF

import copy
import itertools

import globalvar as GlobalVar


def funcCreatNoteDic (capo=0 , tuningName = "standard", maxAvailableFret = 12, printFingerboard = False):
# def funcCreatNoteDic (capo=0 , tuning = [64, 59, 55, 50, 45, 40], maxAvailableFret = 12, printFingerboard = False):
    """ 2019/07/08
        version 0.0
    """
    """ for normal guitar tuning. (E4, B3, G3, D3, A2, E2)
                          string    1   2   3   4   5   6
    in real world physical way, it looks like left-right-reversed
    capo = 1
    """
    # set tuning
    if tuningName == "standard":
        tuning = [64, 59, 55, 50, 45, 40]
    elif tuningName == "Dropped D":
        tuning = [64, 59, 55, 50, 45, 38]
    else:
        print("Tuning name is not correct, or hasn't been set to funcCreatNoteDic.")

    print("capo = " + str(capo)) if printFingerboard == True else None
    print("tuning = " + str(tuning))  if printFingerboard == True else None
    # set 0 fret initial note -- AKA guitar tuning
    arrayFingerBoard = [tuning]
    arrayFingerBoard = [[string+capo for string in arrayFingerBoard[0]]]

    for fret in range (maxAvailableFret - capo):
        arrayFingerBoard.append([string+1 for string in arrayFingerBoard[-1]])

    if printFingerboard == True :
        # print out Finger Board
        print("Notes in Finger board:")
        # print("string 1 to 6")
        arrayFingerBoardTranspose = map(list, zip(*arrayFingerBoard))
        for string in arrayFingerBoardTranspose:
            print(string)


    # create a dictionary: note - position
    # input : note number, ex: 66
    # output: position, ex: [[1, 1], [2, 6], [3, 10]]
    # def funCreatNoteDic (arrayFingerBoard):
    dicNoteOnFingerBoard = {}
    for fret in range(len(arrayFingerBoard)):
        for string in range(6):
            note = arrayFingerBoard[fret][string]
            if note not in dicNoteOnFingerBoard:
                dicNoteOnFingerBoard[note] = [[string+1, fret]] # let string = 1~6
            else:
                dicNoteOnFingerBoard[note].append([string+1, fret]) # let string = 1~6
    return dicNoteOnFingerBoard




def MidiCategorize(MidiFileName, trackChoice = 0):
    # from mido import MidiFile
    mid = MidiFile(MidiFileName)
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        if i == trackChoice:
            print('choose track ' + str(i))
            a = 0
            midiArray= []
            dicCurrentNote = {}
            currentTime = 0
            for msg in track:
                if msg.type[:4] == "note":
                    currentTime = currentTime + msg.time
                    if msg.type == "note_on":
                        # solve continuous same note note-on
                        # assign next start-time as previous stop time if stop time not assigned
                        try:
                            if midiArray[dicCurrentNote[msg.note]][2] =='OffsetNotYetGiven':
                                midiArray[dicCurrentNote[msg.note]][2] = currentTime
                        except:
                            None

                        midiArray.append([msg.note, currentTime, 'OffsetNotYetGiven', 'CatNotYetGiven', 'eventNotGiven'])
                        dicCurrentNote[msg.note] = len(midiArray)-1 # save this number of row
                    elif msg.type == "note_off":
                        midiArray[dicCurrentNote[msg.note]][2] = currentTime # change thie offsetTime by its onset row
    midiArray.append([0, currentTime+999, currentTime+1000, 'dummy line', 'dummy line'])

    """ A function to add count to a dictionary
    """
    def dicAddCount(event, dic):
        if event in dic:
            dic[event] = dic[event] + 1
        else:
            dic[event] = 1

    rowCount = 0
    lenArray = len(midiArray)
    eventNumber = 0
    dicEvent = {}
    while rowCount in range(lenArray):

        # process the 1st event
        midiArray[rowCount][4] = eventNumber
        dicAddCount(eventNumber, dicEvent) # count the event number
        start = midiArray[rowCount][1] # assign event start time
        end   = midiArray[rowCount][2] # assign event end time

        # initialize for sweeping following notes
        rowCount = rowCount + 1
        chordFlag = 1 # initialize chordFlag
        contEventCount = 1

        # sweeping following notes
        while rowCount in range( lenArray ):

            # check the following notes are overlap or not
            if midiArray[rowCount][1] < end:
                midiArray[rowCount][4] = eventNumber # categorized as same event
                dicAddCount(eventNumber, dicEvent) # FUNC: count the event number
                contEventCount = contEventCount + 1 # cumulative count the continuous event

                # if one of the following notes have different start or end time,
                # this event is no longer a CHORD anymore.
                # --> disable chord flag
                if (midiArray[rowCount][1] - start != 0) or (midiArray[rowCount][2] - end != 0):
                    chordFlag = 0

                # update event end time, see the overall-overlapped range
                end = max(end, midiArray[rowCount][2])
                rowCount = rowCount + 1 # step foward

            # if following note isn't overlapped, call it a new event
            else:
                eventNumber = eventNumber + 1 # next event

                # determine category of previous event
                if contEventCount == 1:
                    midiArray[rowCount -1 ][3] = 'MEL' # melody
                elif chordFlag == 1:
                    for row in range(rowCount -contEventCount , rowCount):
                        midiArray[row][3] = 'CHO' # chord
                else:
                    for row in range(rowCount -contEventCount , rowCount):
                        midiArray[row][3] = 'MIX' # mix = chord + melody
                break # break while
    return (midiArray, dicEvent)


"""
    CSP - Constraint satisfaction problems
    used for Chord fingering
    need to import
        from funcMidi import funcCreatNoteDic
        import copy
        import itertools
"""


# input note, output domain
def funcNote2Domain(note, dicNoteOnFingerBoard):
    fingerings = dicNoteOnFingerBoard[note]
    domain = []
    for fingering in fingerings:
        # fingering = [5,2]
        if fingering[1] == 0: # if fret=0, no need swap all fingers
            domain.append(fingering + [0])
        else: # if fret !=0, swap all fingers 1~4
            for finger1234 in range (1,5):
    #                 print(finger1234)
                domain.append(fingering + [finger1234])
    return domain

# input choNote, output domains
# funcNoteDomains
def funcNoteDomains(choNote, dicNoteOnFingerBoard):
    domains = []
    for note in choNote:
        domain = funcNote2Domain(note, dicNoteOnFingerBoard)
        domains.append(domain)
    return domains

# ------ divided into subFunc,
# let MEL to use the same function "funcNote2Domain" -----
# 2019/07/20 07:42
# def funcNoteDomains(choNote, dicNoteOnFingerBoard):
#     domains = []
#     x = 0 # variable
#     for x in range(len(choNote)):
#         # x = 41
#         domains.append([])
#         fingerings = dicNoteOnFingerBoard[choNote[x]]
#         # fingerings = [[5, 2], [6, 7]]
#         for fingering in fingerings:
#             # fingering = [5,2]
#             if fingering[1] == 0: # if fret=0, no need swap all fingers
#                 domains[x].append(fingering + [0])
#             else: # if fret !=0, swap all fingers 1~4
#                 for finger1234 in range (1,5):
#     #                 print(finger1234)
#                     domains[x].append(fingering + [finger1234])
#     return domains


def dicAppend(key, value, dic):
    if key in dic:
        dic[key].append(value)
    else:
        dic[key] = [value]

def funcCSP(domains):
    dicCombination = {} # "legal" combinations after DPC algorithm
    dn = 0 # domain number

    for dn in range(len(domains) -1): # domain number
        for pn in range(len(domains[dn])): # position number
            # sdn: sub-domain number, starting from the next domain
            for sdn in range(dn+1, len(domains)):

                for spn in range(len(domains[sdn])):
                    # constraints

    #               # c0: see this position is already been justified as usable, then skip
                    string0 = domains[dn][pn][0]
                    string1 = domains[sdn][spn][0]
                    # c1: one note per string
                    if string0 != string1:
                        finger0 = domains[dn][pn][2]
                        finger1 = domains[sdn][spn][2]
                        fret0 = domains[dn][pn][1]
                        fret1 = domains[sdn][spn][1]
                        fingerDiff = finger0 - finger1 # finger difference
                        absFingerDiff = abs(fingerDiff)
                        fretDiff = fret0 - fret1
                        absFretDiff = abs(fretDiff)
                        stringDiff = string0 - string1
                        absStringDiff = abs(stringDiff)
                        # fret0, no limitation
                        if fret0 == 0 or fret1 == 0:
                            dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                        # c4*: the same fret
                        elif fret0 == fret1:
                            #  c4: barre index
                            if finger0 == finger1 ==1:
                                dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                            # c4-1: same fret: lower finger press higher "strings"
                            elif (string0 - string1)*(finger0 - finger1) < 0:
                                # constraints: finger(1,2) cannot cross string(1,6)
                                if (finger0 ==1 or finger1 ==1) and (finger0 ==2 or finger1 ==2):
                                    if absStringDiff != 5:
                                        dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                else:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)

                        # c2: higher finger press higher frets
                        #     finger0 is stronger
                        elif (fret0 - fret1) <0:
                            if finger0 == 1:
                                if finger1 == 2 and 0 < (-fretDiff) <= 2:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger1 == 3 and 0 < (-fretDiff) <= 3:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger1 == 4 and 0 < (-fretDiff) <= 4:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                            elif finger0 == 2:
                                if finger1 == 3 and 0 < (-fretDiff) <= 1:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger1 == 4 and 0 < (-fretDiff) <= 3:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                            elif finger0 == 3:
                                if finger1 == 4 and 0 < (-fretDiff) <= 1:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                        elif (fret0 - fret1) >0:
                        # when finger1 stronger than finger0
                            if finger1 == 1:
                                if finger0 == 2 and 0 < (fretDiff) <= 2:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger0 == 3 and 0 < (fretDiff) <= 3:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger0 == 4 and 0 < (fretDiff) <= 4:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                            elif finger1 == 2:
                                if finger0 == 3 and 0 < (fretDiff) <= 1:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                                elif finger0 == 4 and 0 < (fretDiff) <= 3:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
                            elif finger1 == 3:
                                if finger0 == 4 and 0 < (fretDiff) <= 1:
                                    dicAppend((dn,sdn),(domains[dn][pn], domains[sdn][spn]),dicCombination)
    return dicCombination


# Preprocessing: Adversary kill method. Non-lambda version. (Mao)
def funcAdversarykill(dicCombination):
    for loop in range(2):

        # 測試用. 目前做一次不乾淨，要做兩次
        if loop == 1:
            dicCombination = copy.deepcopy(result)


        Keys = dicCombination.keys()
        flatKey = sum(Keys, ())
        uniqueKey = set(flatKey)

        matchDict = {}
        for uniKey in uniqueKey:
#             print (uniKey)
            sets = []
            for key in Keys:
                if uniKey in key:
                    indexLoc = key.index(uniKey)
                    sets.append(set(map(tuple, list(zip(*dicCombination[key]))[indexLoc])))
#             print (set.intersection(*sets))
            matchDict[uniKey] = set.intersection(*sets)

        result = {}
        for k in dicCombination:
            result_temp = []
            compare1 = matchDict[k[0]]
            compare2 = matchDict[k[1]]
            for item in dicCombination[k]:
                if tuple(item[0]) in compare1 and tuple(item[1]) in compare2:
                    result_temp.append(item)
            result[k] = result_temp
    return result, matchDict

# cartisian product -- matchDict
def funcChordSol(dicCombPreproc, matchDict):
# NEED import itertools

    listMatchDict = []

    for key, value in matchDict.items():
        listMatchDict.append(list(value))

    listCartisianProduct = []
    for iterItem in itertools.product(*listMatchDict):
        listItem = []
        for tupleItem in iterItem:
            listItem.append(list(tupleItem))
        listCartisianProduct.append(listItem)

    def rmCandidate():
        for i in range(lenSol):
            for j in range(i+1, lenSol):
                candPair = (candidate[i], candidate[j])
                if i ==1 and j == 2:
#                 if ( candPair ) not in dicCombPreproc[(i, j)]:
                    return False
        return True

    lenSol = len(listCartisianProduct[0])

    def judgeCandidateIn(candidate):
        lenCand = len(candidate)
        for i in range(lenCand):
            for j in range(i+1, lenCand):
                candPair = (candidate[i], candidate[j])
                if ( candPair ) not in dicCombPreproc[(i, j)]:
                    return False
        return True

    def delFaultBarreIndex(candidate):
        oneCount = 0 # index finger counter
        indexFingerCount = 0
        fret = []
        indexFingerFret = []

        # 食指數目>1 and 食指的數目 < 食指fret的數目, 就代表有其他手指按了封閉的fret --> false
        for position in candidate:
            if position[2] == 1:
                indexFingerCount = indexFingerCount + 1
                indexFingerFret.append(position[1])

        uniqFret = list(set(indexFingerFret))
        if len(uniqFret) > 1:
            # print("Index finger presses more than 1 fret. --> Error")
            return False
        # 20190725 bug-fixed
        # if no indexfinger, True
        elif len(uniqFret) ==0:
            return True
        elif len(uniqFret) ==1:
            uniqFret = uniqFret[0]

        fretCount = sum([1 for x in candidate if x[1]==uniqFret])
        if fretCount > indexFingerCount > 1:
            return False
        else:
            return True

    solutions = [x for x in listCartisianProduct if judgeCandidateIn(x)]
    solutions = [x for x in solutions if delFaultBarreIndex(x)]
    return solutions


# package: Chord solution
# add output: costChord
def funcChordSolution(choNote, dicNoteOnFingerBoard):
    domains = funcNoteDomains(choNote, dicNoteOnFingerBoard)
    dicCombination = funcCSP(domains)
    dicCombPreproc, matchDict = funcAdversarykill(dicCombination)
    chordSolution = funcChordSol(dicCombPreproc, matchDict)
    return chordSolution




"""
MELODY best path searching
Theorism
Weight(p,q) = ALONG(p,q) + ACROSS(p,q)
ALONG(p,q) = fret_stretch(p,q) + locality(p,q)

Code:
cost = costAlong + costAcross
costAlong = costStretch + costLocal
"""


# cost Stretch

def funcCalCostAlong(pos0, pos1):
    finger0 = pos0[2]
    finger1 = pos1[2]
    fret0   = pos0[1]
    fret1   = pos1[1]
    string0 = pos0[0]
    string1 = pos1[0]

    # The same position
    if pos0 == pos1:
        costStretch = GlobalVar.get_costSamePosition()
    elif finger0 ==0 or finger1 ==0:
        costStretch = GlobalVar.get_costAlongFinger0()
    # same finger same string, "slide"
    elif finger0 == finger1 and string0 == string1:

        if fret0 == fret1: # string different (if string the same, it is the first condition)
            if finger0 ==1:
                costStretch = GlobalVar.get_costFinger1SameFret()
            else:
                costStretch = GlobalVar.get_costFinger234SameFret()

        # ----- fret different -----
        # finger1 is easy to slide upward
        # but not as much as finger2 & 3 to slide downward
        elif finger0 == 1:
            if fret0 > fret1:
                costStretch = GlobalVar.get_costFinger1SlideDown()
            else:
                costStretch = GlobalVar.get_costFinger1SlideUp()
        elif finger0 == 2 or finger0 ==3:
            if fret0 > fret1:
                costStretch = GlobalVar.get_costFinger23SlideDown()
            else:
                costStretch = GlobalVar.get_costFinger23SlideUp()
        elif finger0 == 4:
            if fret0 > fret1:
                costStretch = GlobalVar.get_costFinger4SlideDown()
            else:
                costStretch = GlobalVar.get_costFinger4SlideUp()
    # same finger shift according to its distance
    elif finger0 == finger1 and string0 != string1:
        deltaPhysical = abs(string0 -string1) + abs(fret0 - fret1)
        costStretch = GlobalVar.get_costFingerShiftSlide() * deltaPhysical
    # Other combinations
    else:
        costStretch = funcCostFinger(pos0, pos1, plot=False)

    # cost Along = costStretch + costLocality
    costAlong = costStretch + GlobalVar.get_costLocalWeight()*(pos0[1]+pos1[1])
    return costAlong

def funcCalCostAcross(pos0, pos1):
    finger0 = pos0[2]
    finger1 = pos1[2]
    fret0   = pos0[1]
    fret1   = pos1[1]
    string0 = pos0[0]
    string1 = pos1[0]

    # fingero (fret0) has min cost
    if finger0 ==0 or finger1 ==0:
        costAcross = GlobalVar.get_costAcrossMeet()
    elif fret0 == fret1:
        # smaller finger press lower string
        if (finger0 - finger1) * (string0 - string1) < 0:
            costAcross = GlobalVar.get_costAcrossMeet()
        else:
            costAcross = GlobalVar.get_costAcrossOut()
    else:
        deltaPhysical = abs(string0 -string1) + abs(fret0 - fret1)
        # default:
        # costAcrossMeet = 0.25
        # cost AcrossOut = 0.5
        costAcross = GlobalVar.get_costAcrossMeet() if abs(finger0-finger1) == deltaPhysical else GlobalVar.get_costAcrossOut()
    return costAcross





# costStretch between finger1 and finger2
# costStretch between finger1 and finger2
def funcCostFinger(pos0, pos1, plot=False):
    finger0 = pos0[2]
    finger1 = pos1[2]
    fret0 = pos0[1]
    fret1 = pos1[1]
    sign = -1 if finger0 > finger1 else 1

    deltaFret = fret1 - fret0
    absDeltaFinger = abs(finger0-finger1)

    if (finger0 == 0 or finger1 == 0):
        # costStretch = 0.5
        print("It should not enter this condition, funcCostFinger or funcCalCostAlong should be wrong")
        costStretch = GlobalVar.get_costBetwFret0andOther()
    elif (finger0 == finger1):
        print("It should not enter this condition, funcCostFinger or funcCalCostAlong should be wrong")
        costStretch = GlobalVar.get_costBetwFret0andOther()
    else:
        #  ********** PWL parameter ***********
        # pwl = [[-1,1,2], [5, 0.5, 2]]
        pwl = [[-1,absDeltaFinger,absDeltaFinger+1], [5, 0.5, 2]]
        pwl = [[-10, -1,absDeltaFinger,absDeltaFinger+1, 10], [10, 5, 0.5, 2, 5]]
        pwl = np.array(pwl)
        pwl[0,:] = pwl[0,:]*sign
        pwl = pwl[:,pwl[0,:].argsort()] # sorting by x value

        costStretch = np.interp(deltaFret, pwl[0,:], pwl[1,:], left=pwl[1,0], right=pwl[1,-1])


    if plot:
        x = np.linspace(-5, 5, 11)
        if (finger0 == 0 or finger1 == 0):
            plt.plot(x, [0.5]*len(x))
        elif finger0 == finger1:
            return costStretch
        else:
            y = np.interp(x, pwl[0,:], pwl[1,:], left=pwl[1,0], right=pwl[1,-1])
            plt.plot(x,y)

        plt.title("Finger" + str(finger0) + " to Finger" + str(finger1))
        plt.xlabel("delta fret")
        plt.ylabel("cost")
        plt.xticks(np.arange(min(x), max(x)+1, 1.0))
        plt.grid(True)
        plt.ylim(0,10)
    return costStretch


# Draw Cost of Stretch Figure
def drawCostStretchFigure():
    pos0 = [3,5,4]
    pos1 = [3,6,1]
    plt.subplots(figsize=(16, 10))
    plt.tight_layout()
    # plt.subplots_adjust(left=0.2, bottom=0.1, right=0.8, top=0.8,hspace=0.5)
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9,hspace=0.5)
    for i in range(4):
        for j in range(4):
    #         print((i % 4)*4 + ( j % 4) + 1)
            if i != j:
                plt.subplot(4,4, (i % 4)*4 + ( j % 4) + 1)
                funcCostFinger([3,5, i], [3, 5, j], plot=True)
    fig = plt.gcf()
    plt.figure(figsize=(40,20))
#     fig.savefig('cost_of_stretching_20190808.png', dpi=100)


# Calculate melody transition cost
# rename: funcCalMelCost -> funcCalMelCostMatrix
def funcCalMelCostMatrix(event0Possible, event1Possible):
    costMatrixUnit = []
    for pos0 in event0Possible:
        pos0beg =[]
        for pos1 in event1Possible:

            # cost is putting here
            # initialise cost
            # costStretch = float("inf")
            # costLocal = float("inf")
            # maybe write a function, input is pos0 and pos1
            costAlong  = funcCalCostAlong(pos0, pos1)
            costAcross = funcCalCostAcross(pos0, pos1)
            cost = costAlong + costAcross

            pos0beg.append(cost)
        costMatrixUnit.append(pos0beg)
    return costMatrixUnit




# 計算chord的cost 2019/07/23
# funcCalChordCost


def funcCalChordCost(oneChord):
    costChordTotal = 0
    # 1: cost between 2 fingers
    numNotes = len(oneChord)
    numFinger1 = 0
    for pos in oneChord:
        numFinger1 = numFinger1 + 1 if pos[2] == 1 else numFinger1
    # 有食指封閉就+0
    costFinger1 = 0
    if numFinger1 > 1:
        costFinger1 = costFinger1 + GlobalVar.get_costChordFinger1()
        # 有封閉加其他指頭
        if numNotes > numFinger1:
            costFinger1 = costFinger1 + GlobalVar.get_costChordFinger1withOther()
    # 2: local locality and (global) locality
    frets = [x[1] for x in oneChord]
    npFrets = np.array(frets)
    maxFret = np.max(npFrets)
    if maxFret != 0:
        minFret = np.min(np.nonzero(npFrets)) # avoid fret0 has high cost
    else:
        minFret = 0
    # maxFret = max([x[1] for x in oneChord])
    # minFret = [x[1] for x in oneChord]

    costLocalLocality = (maxFret - minFret) * GlobalVar.get_costChordLocalWeight()
    costGlobalLocality = maxFret * GlobalVar.get_costChordGlobalWeight()

    #3 strong and weak finger, and finger number used
    costFingers = 0
    for pos in oneChord:
        finger = pos[2]
        if finger == 4:
            costFingers = costFingers + GlobalVar.get_costChordFinger4()
        else:
            costFingers = costFingers + GlobalVar.get_costChordFinger123()
    costFingers = costFingers * GlobalVar.get_costChordFingerWeight()

    # 4 avoid too crowed
    costCrowd = 0
    row0Count = 0
    while row0Count in range(numNotes):
        string0 = oneChord[row0Count][0]
        fret0 = oneChord[row0Count][1]
        finger0 = oneChord[row0Count][2]
        row1Count = row0Count + 1
        while row1Count in range(numNotes):
            string1 = oneChord[row1Count][0]
            fret1 = oneChord[row1Count][1]
            finger1 = oneChord[row1Count][2]

            # same fret, but not finger1(barre), or any one is finger0
            if fret0 == fret1 and not ((finger0 == finger1 == 1) or (finger0 ==0 or finger1 ==0 ) ):
                if abs(string1 - string0 ) < abs(finger1 - finger0):
                    costCrowd = costCrowd + 1
            row1Count = row1Count + 1
        row0Count = row0Count + 1
    costCrowd = costCrowd * GlobalVar.get_costChordCrowdWeight()

    # Overall cost
    costChordTotal = costFinger1 + costLocalLocality + costGlobalLocality + costFingers + costCrowd
    return costChordTotal


"""
Final Integration
Through all MEL, CHO, MIX
"""

def dicNameNotes(notes):
    # input example: dicNameNotes([45, 63])
    # output example: ['A2', 'D#4']
    names = []
    for note in notes:
        modNote = note % 12
        if modNote == 0:
            names.append('C'+str(note//12-1))
        elif modNote ==1:
            names.append('C#'+str(note//12 -1))
        elif modNote ==2:
            names.append('D'+str(note//12 -1))
        elif modNote ==3:
            names.append('D#'+str(note//12 -1))
        elif modNote ==4:
            names.append('E'+str(note//12 -1))
        elif modNote ==5:
            names.append('F'+str(note//12 -1))
        elif modNote ==6:
            names.append('F#'+str(note//12 -1))
        elif modNote ==7:
            names.append('G'+str(note//12 -1))
        elif modNote ==8:
            names.append('G#'+str(note//12 -1))
        elif modNote ==9:
            names.append('A'+str(note//12 -1))
        elif modNote ==10:
            names.append('A#'+str(note//12 -1))
        elif modNote ==11:
            names.append('B'+str(note//12 -1))
    return names


# list by event

def funcMidiEvents(midiArray, calEventNum = float("inf"), fromNumber = 0):
    events = []
    nn = fromNumber
    while nn < len(midiArray) and midiArray[nn][-1] <= calEventNum:
        if midiArray[nn][3] == 'MEL':
            events.append([midiArray[nn][:-1]])
            nn = nn + 1
        elif midiArray[nn][3] == 'MIX' or midiArray[nn][3] == 'CHO':
            subEvents = []
            currentEvent = midiArray[nn][4]
            while nn < len(midiArray) and midiArray[nn][4] == currentEvent and midiArray[nn][-1] <= calEventNum:
                subEvents.append(midiArray[nn][:-1])
                nn = nn + 1
            events.append(subEvents)
        else:
            break
    # unique time
    lastDMY = midiArray[-1][3]
    if lastDMY == 'MIX' or lastDMY == 'MEL' or lastDMY == 'CHO':
        allTime = [x[1:3] for x in midiArray]
    else:
        allTime = [x[1:3] for x in midiArray[:-1] ] # ignore dummy line
    flatAllTime = sum(allTime, [])
    uniqTime = list(set(flatAllTime))
    uniqTime.sort()

    return events, uniqTime



# 依照時間 產生出note 包含tied note
# according to the time, output eventNotes, "tied note" included
def funcArrangeEventNotes(events):
    # print("can I modify it")
    eventsNotes = []
    eventsTimeInfo = []
    for event in events:
        if len(event) == 1: # MEL condition
            eventsNotes.append([event[0][0]])
            eventsTimeInfo.append(event[0][1:3])
        elif event[0][-1] =='CHO':
            choNotes = [x[0] for x in event]
            eventsNotes.append(choNotes)
            eventsTimeInfo.append(event[0][1:3])
        # most complex condition
        # made tied note to be Negative
        elif event[0][-1] == 'MIX':
            allTime = [x[1:3] for x in event]
            flatAllTime = sum(allTime, [])
            uniqTime = list(set(flatAllTime))
            uniqTime.sort()

            subEventNotes = []
#             subTimeInfo = []
            tempNotes = []
#             for time in uniqTime[:-1]:
            for itime in range (len(uniqTime)-1): # 改成number
                time = uniqTime[itime]
                for note in event:
                    if note[1] < time < note[2]:
                        try:
                            tempNotes[tempNotes.index(note[0])] = -note[0]
                        except:
                            pass
                    elif note[1] == time:
                        tempNotes.append(note[0])
                    elif note[2] == time:
                        try:
                            tempNotes.remove(note[0])
                        except:
                            tempNotes.remove(-note[0])
                subEventNotes.append(copy.deepcopy(tempNotes)) # should use deepcopy instead of copy
                eventsTimeInfo.append([time, uniqTime[itime+1]])
            for x in subEventNotes:
                eventsNotes.append(x)


    return eventsNotes, eventsTimeInfo


# run through events
# 有BUG存在!!!
# 目前len = 1的情況下 沒有去判斷延音
def funcNotes2Possibles(eventsNotes, dicNoteOnFingerBoard):
    possible =[]
    for choNote in eventsNotes:
        if len(choNote) == 1 :
            # BUG IS HERE ---------------------------------vvvvvvvvvvvvvv
            if choNote[0] < 0:
                print("BUG, no constraints for tied note when there is only one note")
            possible.append([ [x] for x in funcNote2Domain(abs(choNote[0]), dicNoteOnFingerBoard)])
    #         possible.append([funcNote2Domain(choNote[0], dicNoteOnFingerBoard)])
        else:
            subPossible = funcChordSolution(list(map(abs, choNote)), dicNoteOnFingerBoard)
            possible.append(subPossible)
    # 如果是從前一個就start, 還沒結束的NOte, 改為 -Note (如-55)
    # 當作一個標記flag
    # 算chord solution時要拿abs
    # 可是算path的時候
    # 有看到負號就只能抓前一組相同的note posibtion
    return possible



# @@@@@@@@@ MIX 的版本 @@@@@@@@@
# 從MELODY 摳過來的
# 這邊不能合成function
# 因為要跟MEL 和 CHO 一起混著做
# 這邊只是確定funcCalMixCostMatrix 正確
# cost有先加previous再做運算的正確版


def funcBestPath(eventsNotes, possible, printCostChord = False, printCostTran = False):
    costBest = []

    iniSize = len(possible[0])
    npPreMinValue = np.zeros(iniSize)
    preMinIndex = [[0] for i in range(iniSize)]
    for i in range(len(possible)-1):
        event0Possible = possible[i]
        event1Possible = possible[i+1]
        mixNotes0 = eventsNotes[i]
        mixNotes1 = eventsNotes[i+1]
        # calculate MIX cost
        costMatrixUnitTran, costMatrixUnitChord = funcCalTranCostMatrix(event0Possible, event1Possible, mixNotes0, mixNotes1)
        npCostMatrixUnitTran = np.array(costMatrixUnitTran)
        npCostMatrixUnitChord = np.array(costMatrixUnitChord)

        # add pre value to matrix
        npNewPreCostMatrix = np.zeros([len(npPreMinValue), np.shape(npCostMatrixUnitTran)[1]])
        for rwi in range(len(npPreMinValue)):
            npNewPreCostMatrix[rwi, :] = npPreMinValue[rwi]
        # total cost of this transition
        npCostMatrixUnit = npCostMatrixUnitChord + npCostMatrixUnitTran + npNewPreCostMatrix

        # print each costMatrixUnit independently, for debug
        if (printCostChord or printCostTran):
            # np print won't be limited
            np.set_printoptions(threshold=np.inf)
            print("number = " + str(i))
            if printCostChord:
                print("printCostChord =")
                print(np.around(npCostMatrixUnitChord, decimals = 0))
            if printCostTran:
                print("printCostTran =")
                print(np.around(npCostMatrixUnitTran, decimals = 0))
            print("printCostAll =")
            print(np.around(npCostMatrixUnit, decimals = 0))
            print("")

        # do matrix summary: minValue + minIndex
        npMinValue = np.min(npCostMatrixUnit, axis = 0)
        npMinIndex = np.argmin(npCostMatrixUnit, axis = 0)
        minIndex = list(npMinIndex)

        # initialize for combining with previous event
        npCombMinValue = np.zeros(len(npMinValue))
        combMinIndex = [0 for icmi in range(len(npMinValue))]

        # minValue
        for imin in range(len(npMinValue)):
            npCombMinValue[imin] = npMinValue[imin] + npPreMinValue[npMinIndex[imin]]
            combMinIndex[imin] = copy.deepcopy(preMinIndex[npMinIndex[imin]])
            combMinIndex[imin].append(copy.deepcopy(minIndex[imin]))
        npPreMinValue = npCombMinValue
        preMinIndex = combMinIndex

    #     minSummary = np.vstack
        costBest.append(copy.deepcopy([npCombMinValue,combMinIndex]))
    return costBest
# costBest[-1]



# 這個Function 也可以用在melody to Mix, 不會被限制
# 他也許可以改為funcTranCostUnit, 專門比較transition的cost
def funcCalTranCostUnit(mixPos0, mixPos1,mixNotes0, mixNotes1, printOut = False):

    costTran = 0
    costAlongAll = 0
    costAcrossAll = 0
    costTiedNote = 0
    for ipos0 in range(len(mixPos0)):
#         print("ipos0=" + str(ipos0))
        for ipos1 in range(len(mixPos1)):
#             print("ipos1=" + str(ipos1))
            if mixNotes1[ipos1] < 0:
                costTiedNote = 0 # initialize tied-note
                try:
                    relativeNote0Index = mixNotes0.index(abs(mixNotes1[ipos1]))
                except:
                    relativeNote0Index = mixNotes0.index(   (mixNotes1[ipos1]))
#                 print("relativeNote0Index = " + str(relativeNote0Index))
                if mixPos1[ipos1] != mixPos0[ relativeNote0Index]:
#                     print("negative and !=")
                    costTiedNote = float("inf")
                    break
                # 可以走到這代表前次和這次的position相同
                # costAlong = 0, 所以不用做任何相加
            else:
                costAlong    = funcCalCostAlong(mixPos0[ipos0], mixPos1[ipos1])
                costAcross   = funcCalCostAcross(mixPos0[ipos0], mixPos1[ipos1])
#                 print("mixPos0[0] =" + str(mixPos0[0]))
#                 print("mixPos1[0] =" + str(mixPos1[0]))
#                 print("ipos0 =" + str(ipos0) + ", ipos1 = " + str(ipos1) + ", costAlong=" + str(costAlong))
#                 print("costAcross="+str(costAcross))
                # 先分開測測看
                costAlongAll = costAlongAll + costAlong
                costAcrossAll = costAcrossAll + costAcross
                #原本的是costTrain
#                 costTran = costTran + costAlong + costAcross
    ##### debug use #####
#     if mixPos0 == [[6, 3, 1], [2, 0, 0], [3, 0, 0]] and mixPos1 ==[[6, 3, 1], [4, 0, 0]] :

#     print("costAlong = " + str(costAlongAll))
#     print("costAcross = " + str(costAcrossAll))
    costTran = costAlongAll + costAcrossAll + costTiedNote

    costChord0   = funcCalChordCost(mixPos0)
    costChord1   = funcCalChordCost(mixPos1)
    costChord = (costChord0 + costChord1)* GlobalVar.get_costChordWeight()
#     costMixTotal = costMixTotal+ costChord
#     print(costChord)
    return costTran, costChord

# costMixTotal



# Calculate MIX transition cost

def funcCalTranCostMatrix(event0Possible, event1Possible, mixNotes0, mixNotes1):
    costMatrixUnitTran = []
    costMatrixUnitChord = []
    for mixPos0 in event0Possible:
        pos0beg =[]
        pos0begChord = []
        for mixPos1 in event1Possible:

            # cost is putting here
            costTran, costChord = funcCalTranCostUnit(mixPos0, mixPos1,mixNotes0, mixNotes1)

            # melody: highly dependent to Tran
            # chord: lower dependent to Tran
            if len(mixPos0) > 1 or len(mixPos1) > 1:
                costTran = costTran * 0.25

            pos0beg.append(costTran)
            pos0begChord.append(costChord)
        costMatrixUnitTran.append(pos0beg)
        costMatrixUnitChord.append(pos0begChord)
    return costMatrixUnitTran, costMatrixUnitChord



# Solutions
# 看要不要直接input costBest[-1][1]
# 裡面比較不用寫這麼複雜

def funcSolutions(costBest, possible, printOut=False):
    solutions = []

    print("Best paths of the last stage:") if printOut else None
    for choose in range(len(costBest[-1][1])):
        bestPathNumber = costBest[-1][1][choose][1:]
#         print(bestPathNumber)  if printOut else None
        bestPath = []
        for i in range(len(bestPathNumber)):
            bestPath.append(possible[i][bestPathNumber[i]])
        bestPath.append(possible[-1][choose])
        print("cost=" + '%.2f' % costBest[-1][0][choose] )  if printOut else None
        print(" " + str(bestPath)) if printOut else None
        solutions.append(["cost =", costBest[-1][0][choose], bestPath ])

    choose = np.argmin(costBest[-1][0], axis = 0)
    bestSolution = solutions[choose]
    return solutions, bestSolution


# deal with time signature
# output: timeResolution, quaver, oneBar
def genTimeInfo(uniqTime, printOut = False):
    npUniqTime = np.array(uniqTime)# - uniqTime[:-1]
    diffUniqTime = npUniqTime[1:] - npUniqTime[:-1]
    diffUniqTimeSet = list(set(diffUniqTime)) # suggestion that user can choose for timeResolution
    diffUniqTimeSet.sort()

    timeResolution = 0
    if len(diffUniqTimeSet) == 1:
        timeResolution = diffUniqTimeSet[0]
    else:
        itr = 0
        while timeResolution == 0:
            sta = diffUniqTimeSet[itr]
            if sta != 1:
                for stb in diffUniqTimeSet:
                    if stb != sta:
                        if stb % sta == 0:
                            timeResolution = sta
                            break
            itr = itr + 1

    (val, counts) = np.unique(diffUniqTime, return_counts = True)
    quaver = val[np.argmax(counts)] # assume that most common time interval is the quaver (8th note)
    oneBar = 8* quaver
    if printOut == True:
        print("for debug usage:")
        print("npUniqTime = " + str(npUniqTime))
        print("diffUniqTime = " + str(diffUniqTime))
        print("diffUniqTimeSet =" + str(diffUniqTimeSet))
        print("outputs:")
        print("timeResolution =" + str(timeResolution))
        print("quaver =" + str(quaver))
        print("oneBar =" + str(oneBar))
    return timeResolution, quaver, oneBar, npUniqTime


# get print arrays, save into array, both horizontal and vertical
def genPrintArray(eventsNotes, eventsTimeInfo, npUniqTime, bestSolution, timeResolution = 32, oneBar = 1024, numPrintBar = 1):
    # timeResolution = 32
    # numPrintBar = 1
    # 用eventsTimeInfo 去掃
    printEventsNotes = copy.deepcopy(eventsNotes)
    printEventsTimeInfo = copy.deepcopy(eventsTimeInfo)
    printBestSolution = copy.deepcopy(bestSolution[2])

    verticalPrintArray = []
    horizontalPrintArrayUnit = []
    horizontalPrintArray = []
    v6 = [" | " for x in range(6) ]
    d6 = [" . " for x in range(6) ]
    s5 = [" " for x in range(2) ]
    tempV = copy.deepcopy(v6)
    tempV.extend(s5)
    tempV.extend(copy.deepcopy(v6))
    tempD = copy.deepcopy(d6)
    tempD.extend(s5)
    tempD.extend(copy.deepcopy(d6))


    printStatus = npUniqTime[0]
    prePrintStatus = -1 # initialize prePrintStatus
    if bestSolution[-1] == "standard":
        verticalPrintArray.append([" E  A  D  G  B  E          Fingerings"])
    elif bestSolution[-1] =="Dropped D":
        verticalPrintArray.append([" D  A  D  G  B  E          Fingerings"])
    for timeInfo in eventsTimeInfo:
        start = timeInfo[0]
        end = timeInfo[1]

        # print bar
        if (printStatus // oneBar) > (prePrintStatus // oneBar):
            verticalPrintArray.append(["------------------     ------------------"])
            horizontalPrintArrayUnit.append(tempV)

        # if print Vertically, choose how many bars per row
#         if printStatus % (oneBar * numPrintBar) == 0 : # bug: printStatus is not necessary integer steps
        if ((printStatus // (oneBar * numPrintBar)) > (prePrintStatus // (oneBar * numPrintBar))): # or (printStatus < oneBar*numPrintBar): # bug: printStatus is not necessary integer steps
            horizontalPrintArray.append(horizontalPrintArrayUnit)
            horizontalPrintArrayUnit = []
            if bestSolution[-1] == "standard":
                horizontalPrintArrayUnit.append([" E ", " A ", " D ", " G ", " B ", " E ", "   ", "   ", " R ", " E ", " G ", " N ", " I ", " F "])
            elif bestSolution[-1] =="Dropped D":
                horizontalPrintArrayUnit.append([" D ", " A ", " D ", " G ", " B ", " E ", "   ", "   ", " R ", " E ", " G ", " N ", " I ", " F "])
        prePrintStatus = printStatus # update prePrintStatus

        # print empty time
        while printStatus < start:
            verticalPrintArray.append([" .  .  .  .  .  .       .  .  .  .  .  . "])
            horizontalPrintArrayUnit.append(tempD)
            printStatus = printStatus + timeResolution
        attacked = 0 # after start, keep the cotinous or tied note as " | "
        while printStatus < end:
            strs = [" . " for x in range(6) ]
            fings = [" . " for x in range(6) ]
            strsV = [" . " for x in range(6) ]
            fingsV = [" . " for x in range(6) ]

            for ifingering in range(len(printBestSolution[0])):
                fingering = printBestSolution[0][ifingering]
                note = printEventsNotes[0][ifingering]
                if note < 0: # Tied note
                    strs[fingering[0]-1] = " | "
                    fings[fingering[0]-1] = " | "
                    strsV[fingering[0]-1] = "---"
                    fingsV[fingering[0]-1] = "---"

                elif attacked == 0:
                    strs[fingering[0]-1] =  " " + str(fingering[1]) + " " if len(str(fingering[1])) == 1 else " " + str(fingering[1])
                    fings[fingering[0]-1] = " " + str(fingering[2]) + " "
                    strsV[fingering[0]-1] = " " + str(fingering[1]) + " " if len(str(fingering[1])) == 1 else " " + str(fingering[1])
                    fingsV[fingering[0]-1] = " " + str(fingering[2]) + " "
                else:
                    strs[fingering[0]-1] = " | "
                    fings[fingering[0]-1] = " | "
                    strsV[fingering[0]-1] = "---"
                    fingsV[fingering[0]-1] = "---"
            attacked = 1


            printStatus = printStatus + timeResolution
            strsV.reverse()
            tempHorizontalPrint = copy.deepcopy(strsV)
            tempHorizontalPrint.extend(s5)
            fingsV.reverse()
            tempHorizontalPrint.extend(fingsV)

            horizontalPrintArrayUnit.append(tempHorizontalPrint)

            tempVerticalPrint = [x for x in reversed(strs)]
            tempVerticalPrint.extend(["     "])
            tempVerticalPrint.extend([x for x in reversed(fings)])
            verticalPrintArray.append(tempVerticalPrint)
        # after printed, del element
        del printEventsNotes[0]
        del printEventsTimeInfo[0]
        del printBestSolution[0]

    horizontalPrintArray.append(horizontalPrintArrayUnit)
    del horizontalPrintArray[0] # delete first empty row
    return verticalPrintArray, horizontalPrintArray

#  print solution, horizontal or vertical
def printSolution(verticalPrintArray, horizontalPrintArray, printDirection = "horizontal"):

    if printDirection == "horizontal":
        print('\x1b[1m') # bold font
#         for block in horizontalPrintArray[1:]:
        for block in horizontalPrintArray:
            blockT = list(zip(*block))

            for i in range(len(blockT)-1,-1,-1): # reversed(blockT):
                line = blockT[i]
                print("==="*len(line)) if i == len(blockT)-1 else None
#             for line in reversed(blockT):
                print(*line, sep="")

            # it's hard to tell how long the first row is
            # so if not getting the first line, just hard print a fixed "======="
            try:
                print("==="*len(line))
            except:
                print("===================================")
    elif printDirection == "vertical":
        print('\x1b[1m')
        for line in (verticalPrintArray):
            print(*line, sep="")



# print to pdf file
def printPDF(verticalPrintArray, horizontalPrintArray, outputPdfName = "guitarFingering.pdf", printDirection = "horizontal", rowsPerPage = 3, linespace = 5):
    # from fpdf import FPDF
#     rowsPerPage = 3
#     printDirection = "horizontal"
    pdf = FPDF()
    pdf.set_left_margin(1)#margin: float)
    pdf.set_top_margin(1)#margin: float)
    # pdf.add_page()
    pdf.set_font("courier", "B", size=10)
#     linespace = 5

    rows = 0
    if printDirection == "horizontal":
#         for block in horizontalPrintArray[1:]:
        for block in horizontalPrintArray:

            pdf.add_page() if rows % rowsPerPage == 0 else None
            blockT = list(zip(*block))

            for i in range(len(blockT)-1,-1,-1): # reversed(blockT):
    #         for line in reversed(blockT):
                line = blockT[i]
                pdf.cell(0, linespace, txt = "==="*len(line), ln=1) if i == len(blockT)-1 else None
                pdf.cell(0, linespace, txt="".join(line), ln=1)
            pdf.cell(0, linespace, txt = "==="*len(line), ln=1)
            rows = rows + 1

    elif printDirection == "vertical":
        pdf.add_page()
        for line in (verticalPrintArray):
            pdf.cell(0, linespace, txt = "".join(line), ln=1)
    pdf.output(outputPdfName)
