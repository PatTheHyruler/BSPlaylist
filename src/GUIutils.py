import json

with open("PlInfoMsg.json", "r") as f:
    PlInfoMsgDict = json.load(f)


def update_names(window, playlist):
    songupdatelist = []
    for i in playlist.get_names():
        songupdatelist.append([i, "placeholder"])
    window["-SONG TABLE-"].update(values=songupdatelist)


def set_layout_song_list(window):
    window[f'-COL1-'].update(visible=False)
    window[f'-COL2-'].update(visible=True)


def reset_layout(window):
    window[f'-COL1-'].update(visible=True)
    window[f'-COL2-'].update(visible=False)


def update_pl_info_msg(window, index, pl_info_msg_dict=PlInfoMsgDict):
    window["-PL INFOMSG-"].update(pl_info_msg_dict[str(index)])


def reset_ui(window):
    update_pl_info_msg(window, 0)
    reset_layout(window)
