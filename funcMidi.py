

def funcCreatNoteDic (capo=0 , tuning = [64, 59, 55, 50, 45, 40], maxAvailableFret = 12):
    """ 2019/07/08
        version 0.0
    """
    """ for normal guitar tuning. (E4, B3, G3, D3, A2, E2)
                          string    1   2   3   4   5   6
    in real world physical way, it looks like left-right-reversed
    capo = 1
    """
    print("capo = " + str(capo))
    print("tuning = " + str(tuning))
    # set 0 fret initial note -- AKA guitar tuning
    arrayFingerBoard = [tuning]
    arrayFingerBoard = [[string+capo for string in arrayFingerBoard[0]]]

    for fret in range (maxAvailableFret - capo):
        arrayFingerBoard.append([string+1 for string in arrayFingerBoard[-1]])

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




def MidiCategorize(MidiFileName):
    from mido import MidiFile
    mid = MidiFile(MidiFileName)
    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        a = 0
        midiArray= []
        dicCurrentNote = {}
        currentTime = 0
        for msg in track:
            if msg.type[:4] == "note":
                currentTime = currentTime + msg.time
                if msg.type == "note_on":
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
import copy
import itertools

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
        if len(uniqFret) != 1:
            # print("Index finger presses more than 1 fret. --> Error")
            return False
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
def funcChordSolution(choNote, dicNoteOnFingerBoard):
    domains = funcNoteDomains(choNote, dicNoteOnFingerBoard)
    dicCombination = funcCSP(domains)
    dicCombPreproc, matchDict = funcAdversarykill(dicCombination)
    chordSolution = funcChordSol(dicCombPreproc, matchDict)
    return chordSolution
