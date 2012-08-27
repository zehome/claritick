import dialog
from django.conf import settings

try:
    # absolute path to executable or name of executable'
    DIALOG = str(settings.DIALOG_DIALOG)
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
# choices are in the form (tag, item)
def dialog_menu(msg, choices):
    return D.menu(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))


# choices are in the form (tag, item, status) and status is boolean
def dialog_radiolist(msg, choices):
    return D.radiolist(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))


def dialog_msgbox(msg):
    return D.msgbox(msg, width=WIDTH, height=HEIGHT)


def dialog_scrollbox(msg):
    return D.scrollbox(msg, width=WIDTH, height=HEIGHT)


def dialog_yesno(msg, default):  # 'default' is initial value of boolean type
    return int(not D.yesno(msg, width=WIDTH, height=HEIGHT,
               defaultno=not default))


# default is initial string
def dialog_inputbox(msg, default):
    return D.inputbox(msg, width=WIDTH, height=HEIGHT, init=str(default))


 # choices are in the form (tag, item, status) and status is boolean
def dialog_checklist(msg, choices):
    return D.checklist(msg, width=WIDTH, height=HEIGHT, choices=tuple(choices))
