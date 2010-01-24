import dialog
from django.conf import settings

try:
    DIALOG = str(settings.DIALOG_DIALOG) # absolute path to executable or name of executable'
except AttributeError:
    DIALOG = 'dialog'
try:
    DIALOGRC = str(settings.DIALOG_DIALOGRC)
except AttributeError:
    DIALOGRC = None
try:
    HEIGHT = int(settings.DIALOG_HEIGHT)
except AttributeError:
    HEIGHT = 0
try:
    WIDTH = int(settings.DIALOG_WIDTH)
except AttributeError:
    WIDTH = 0
D = dialog.Dialog(dialog=DIALOG, DIALOGRC=DIALOGRC)
try:
    D.setBackgroundTitle(str(settings.DIALOG_BACKGROUND_TITLE))
except AttributeError:
    pass

### These dialog_* methods shows DIALOG on the screen
def dialog_menu(msg, choices): # choices are in the form (tag, item)
    return D.menu(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))

def dialog_radiolist(msg, choices): # choices are in the form (tag, item, status) and status is boolean
    return D.radiolist(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))

def dialog_msgbox(msg):
    return D.msgbox(msg, width=WIDTH, height=HEIGHT)

def dialog_scrollbox(msg):
    return D.scrollbox(msg, width=WIDTH, height=HEIGHT)

def dialog_yesno(msg, default): # 'default' is initial value of boolean type
    return int(not D.yesno(msg, width=WIDTH, height=HEIGHT, defaultno=not default))

def dialog_inputbox(msg, default): # default is initial string
    return D.inputbox(msg, width=WIDTH, height=HEIGHT, init=str(default))

def dialog_checklist(msg, choices): # choices are in the form (tag, item, status) and status is boolean
    return D.checklist(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))
