import json

with open("PlInfoMsg.json","r") as f:
    PlInfoMsgDict = json.load(f)

def updateNames(window, playlist):
    songupdatelist = []
    for i in playlist.getNames():
        songupdatelist.append([i, "placeholder"])
    window["-SONG TABLE-"].update(values=songupdatelist)

def setLayoutSonglist(window):
    window[f'-COL1-'].update(visible=False)
    window[f'-COL2-'].update(visible=True)
def resetLayout(window):
    window[f'-COL1-'].update(visible=True)
    window[f'-COL2-'].update(visible=False)
def updatePlInfoMsg(window, index, PlInfoMsgDict=PlInfoMsgDict):
    window["-PL INFOMSG-"].update(PlInfoMsgDict[str(index)])
def resetUI(window):
    updatePlInfoMsg(window,0)
    resetLayout(window)