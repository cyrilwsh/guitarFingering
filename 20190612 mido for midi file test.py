
# coding: utf-8

# In[1]:


from mido import MidiFile
mid = MidiFile('p20190612_midi_test_mix.mid')
mid


# In[2]:


mid.tracks


# In[26]:


for i, track in enumerate(mid.tracks):
    print('Track {}: {}'.format(i, track.name))
    a = 0
    midiArray= []
    dicCurrentNote = {}
    currentTime = 0
    for msg in track:
#         print(a)
#         a+=1
#         print(msg)
        if msg.type[:4] == "note":
            currentTime = currentTime + msg.time
            if msg.type == "note_on":
                midiArray.append([msg.note, currentTime, 'OffsetNotYetGiven', 'CatNotYetGiven', 'eventNotGiven'])
                dicCurrentNote[msg.note] = len(midiArray)-1 # save this number of row
            elif msg.type == "note_off":
                midiArray[dicCurrentNote[msg.note]][2] = currentTime # change thie offsetTime by its onset row
#             print(msg)
# print(dicCurrentNote)
# print(midiArray)
midiArray


# In[39]:


""" A function to add count to a dictionary
"""
def dicAddCount(event, dic):
    if event in dic:
        dic[event] = dic[event] + 1
    else:
        dic[event] = 1


# In[67]:


rowCount = 13
lenArray = len(midiArray)
eventNumber = 0
dicEvent = {}
while rowCount in range(lenArray):
    midiArray[rowCount][4] = eventNumber
    dicAddCount(eventNumber, dicEvent) # count the event number
    start = midiArray[rowCount][1] # assign event start time
    end   = midiArray[rowCount][2] # assign event end time
    rowCount = rowCount + 1
    chordFlag = 1 # initialize chordFlag
    contEventCount = 1
    while rowCount in range( lenArray ):
        if midiArray[rowCount][1] < end: # update if 2-continous notes are overlapped
            midiArray[rowCount][4] = eventNumber # categorized as same event
            dicAddCount(eventNumber, dicEvent) # count the event number
            contEventCount = contEventCount + 1 # cumulative count the continuous event
            
            if (midiArray[rowCount][1] - start != 0) or (midiArray[rowCount][2] - end != 0):
                chordFlag = 0
            end = max(end, midiArray[rowCount][2]) # update event end time
            rowCount = rowCount + 1 # step foward
        else: 
            eventNumber = eventNumber + 1 # next event
            
            if contEventCount == 1:
                midiArray[rowCount -1 ][3] = 'MEL'
            elif chordFlag == 1:
#                 print('enter chord')
#                 print(contEventCount)
                for row in range(rowCount -contEventCount , rowCount):
#                     print(midiArray[row][3])
                    midiArray[row][3] = 'CHO'
            else:
#                midiArray[rowCount  - contEventCount : rowCount][3] = 'MIX'
                for row in range(rowCount -contEventCount , rowCount):
#                     print(midiArray[row][3])
                    midiArray[row][3] = 'MIX'
            break # break while
#     print(end)

#     print(rowCount)
print(midiArray)


# In[42]:


#dicEvent
#for key in dicEvent:
    


# In[37]:


eventDic = {}
for i in range(lenArray):
    if midiArray[i][4] in eventDic:
        eventDic[midiArray[i][4]] = eventDic[midiArray[i][4]] + 1
    else:
        eventDic[midiArray[i][4]] = 1
eventDic


# In[5]:


print(track[6].type)
print(track[6].note)
print(track[6].time)


# In[6]:


import numpy as np
a = np.empty((0,4))
a = np.append(a,[[1,2,3,4]])

a = np.append([a], [[5,6,7,8]],axis=0)
print(a)
a[1,1] = 7.6
# a.shape
print(a)


# In[62]:


b = []
b.append([1,2,3,4])
b.append([5,6,7,8])
# b[0][0] + b[0][1]
b[1].append(2)
b
for row in b:
    row[1] = 1
b


# In[36]:


dicCurrentNote

