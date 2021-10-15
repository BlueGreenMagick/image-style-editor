"""
Anki Add-on: Image Style Editor
"""

import os
import json
import sys
import re
import unicodedata

from aqt import mw
from aqt.editor import EditorWebView, Editor
from aqt.qt import Qt, QWidget, QDesktopWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QLineEdit, QCheckBox, QPushButton
from anki.hooks import addHook, runHook, wrap
from aqt.utils import tooltip, showText

try: 
    from aqt.theme import theme_manager #v2.1.20+
    night_mode = theme_manager.night_mode
except:
    night_mode = False

"""

-hooks: 
EditorWebView.contextMenuEvent, profileLoaded

-wraps: 
Editor.onBridgeCmd

-used methods/variables: 
mw.addonManager.getConfig, mw.addonManager.writeConfig
mw.col.findNotes, mw.col.getNote
mw.col.tags.canonify
mw.progress.start, mw.progress.finish
note.tags, note.fields, note.flush, note.model, note.id, note[field]
editor.note, editor.savenow, editor.loadNote, editor.setNote, editor.web.eval
theme_manager.night_mode

uses pycmd "focus:..." from editor js

"""



VERSION_CP = "2.4"
"""
zzzversion-checkpoint history

~ v2.1.1 temppatch : didn't exist
v2.2 : "2.2"
v2.3 : "2.3"
v2.4: "2.4"
"""

config  = mw.addonManager.getConfig(__name__)
config["zzz-version-checkpoint"] = VERSION_CP
mw.addonManager.writeConfig(__name__, config)


class UI(QWidget):

    def __init__(self, main, editor, img_name, is_occl, curr_fld):
        super(UI, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.editor = editor
        self.image_name = img_name
        self.main = main
        self.config = mw.addonManager.getConfig(__name__)
        self.is_occl = is_occl
        self.curr_fld = curr_fld
        self.attr2qt = {}
        self.styled_prop = ["width", "height", "min-width", "min-height", "max-width", "max-height"]
        self.not_styled_prop = ["Apply to all notes", "Apply to all fields"]
        self.setupUI()
        
    def clicked_ok(self):
        styles = {
            "width": self.widthEdit.text().strip(),
            "height": self.heightEdit.text().strip()
        }
        if self.config["min-size"]:
            styles["min-width"] = self.minWidthEdit.text().strip()
            styles["min-height"] = self.minHeightEdit.text().strip()
        if self.config["max-size"]:
            styles["max-width"] = self.maxWidthEdit.text().strip()
            styles["max-height"] = self.maxHeightEdit.text().strip()

        for s in styles:
            if re.match(r"^\d+?(\.\d+?)?$", styles[s]) is not None:
                styles[s] += "px"
            elif re.match(r"^--.+$", styles[s]) is not None:
                styles[s]  = "var(" + styles[s] + ")"

        # check if occl widgets exists
        try: 
            occl_all_note = self.occlAllNote.isChecked()
            occl_note = True #all occl notes have this widget
        except AttributeError: 
            occl_all_note = False
            occl_note = False
        try:
            occl_all_fld = self.occlAllFld.isChecked()
        except AttributeError:
            occl_all_fld = False 

        if occl_note:
            self.main.occl_modify_styles(styles, occl_all_fld, occl_all_note)
        else:
            self.main.modify_styles(styles)

        self.close()

    def clicked_cancel(self):
        self.close()

    def clicked_defaults(self):
        self.fill_defaults(True)

    def set_prev_styles(self, styles):
        self.prev_styles = styles

    def qt_set_value(self, qtobj, val):
        if type(qtobj) is QLineEdit:
            qtobj.setText(val) 
        elif type(qtobj) is QCheckBox:
            qtobj.setChecked(val)

    def fill_defaults(self, do_style):
        attr2qt = self.attr2qt
        styled = self.styled_prop
        not_styled = self.not_styled_prop
        zdefaults = self.config["zdefaults"]
        for z in zdefaults:
            if z in styled:
                if do_style and z in attr2qt: #falsy default values need to be set too for overriding
                        qtobj = attr2qt[z]
                        self.qt_set_value(qtobj, zdefaults[z])
            elif z in not_styled:
                if z in attr2qt:
                    qtobj = attr2qt[z]
                    self.qt_set_value(qtobj, zdefaults[z])

    def fill_in(self, styles, original):
        self.original = original
        self.fill_defaults(False)

        attr2qt = self.attr2qt
        for a in styles:
            val = styles[a]
            if a in attr2qt:
                qtobj = attr2qt[a]
                self.qt_set_value(qtobj, val)

        for o in original:
            if o == "width":
                self.originalWidth.setText(str(original[o]) + "px")
            elif o == "height":
                self.originalHeight.setText(str(original[o]) + "px")

    def check_valid_input(self, inp):
        valids = ["", "auto", "inherit", "initial", "unset"]
        valid_re = [
            r"^\d+(?:\.\d+)?(?:px|cm|mm|in|pc|pt|ch|em|ex|rem|%|vw|vh|vmin|vmax)?$",
            r"^(?:var|calc|attr)\([\s\S]*\)$",
            r"^--.+$"
            ]
        if inp in valids:
            return True
        else: 
            for r in valid_re:
                if re.match(r, inp) is not None:
                    return True
        return False

    def onchange(self, text, val_label):
        if self.check_valid_input(text):
            if val_label.isVisible():
                val_label.hide()
        else:
            if not val_label.isVisible():
                val_label.show()

    def validate_label(self):
        label = QLabel('Not a valid format!')
        label.setStyleSheet("QLabel {color : red}")
        policy = label.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        label.setSizePolicy(policy)
        label.hide()
        return label

    def hLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def disableLineEdit(self, lineEdit):
        lineEdit.setReadOnly(True)
        if night_mode:
            lineEdit.setStyleSheet("QLineEdit {background-color : #777;}")
        else:
            lineEdit.setStyleSheet("QLineEdit {background-color : lightgrey}")

    def setupUI(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        # add widgets to set height and width
        widthLabel = QLabel('width')
        heightLabel = QLabel('height')
        self.widthEdit = QLineEdit(self)
        self.widthValidate = self.validate_label()
        self.heightValidate = self.validate_label()
        self.widthEdit.textEdited.connect(lambda i, v=self.widthValidate: self.onchange(i, v))
        self.heightEdit = QLineEdit(self)
        self.heightEdit.textEdited.connect(lambda i, v=self.heightValidate: self.onchange(i, v))
        self.attr2qt["width"] = self.widthEdit
        self.attr2qt["height"] = self.heightEdit

        wLayout = QHBoxLayout()
        wLayout.addWidget(widthLabel)
        wLayout.addWidget(self.widthEdit)

        hLayout = QHBoxLayout()
        hLayout.addWidget(heightLabel)
        hLayout.addWidget(self.heightEdit)

        sizeInputLayout = QHBoxLayout()
        sizeInputLayout.addLayout(wLayout)
        sizeInputLayout.addLayout(hLayout)

        labelLayout = QHBoxLayout()
        labelLayout.addWidget(self.widthValidate)
        labelLayout.addWidget(self.heightValidate)

        sizeLayout = QVBoxLayout()
        sizeLayout.addLayout(sizeInputLayout)
        sizeLayout.addLayout(labelLayout)

        # add final layout to main layout
        mainLayout.addLayout(sizeLayout)
        mainLayout.addWidget(self.hLine())

        # add min- sizes and max- sizes
        if self.config["min-size"]:
            minWidthLabel = QLabel("min-width")
            minHeightLabel = QLabel("min-height")
            self.minWidthEdit = QLineEdit(self)
            self.minHeightEdit = QLineEdit(self)
            minLayout = QHBoxLayout()
            minLayout.addWidget(minWidthLabel)
            minLayout.addWidget(self.minWidthEdit)
            minLayout.addWidget(minHeightLabel)
            minLayout.addWidget(self.minHeightEdit)
            self.minWidthEdit.textEdited.connect(lambda i, v=self.widthValidate: self.onchange(i, v))
            self.minHeightEdit.textEdited.connect(lambda i, v=self.heightValidate: self.onchange(i, v))
            self.attr2qt["min-width"] = self.minWidthEdit
            self.attr2qt["min-height"] = self.minHeightEdit
            
            mainLayout.addLayout(minLayout)
            mainLayout.addWidget(self.hLine())

        if self.config["max-size"]:
            maxWidthLabel = QLabel("max-width")
            maxHeightLabel = QLabel("max-height")
            self.maxWidthEdit = QLineEdit(self)
            self.maxHeightEdit = QLineEdit(self)
            maxLayout = QHBoxLayout()
            maxLayout.addWidget(maxWidthLabel)
            maxLayout.addWidget(self.maxWidthEdit)
            maxLayout.addWidget(maxHeightLabel)
            maxLayout.addWidget(self.maxHeightEdit)
            self.maxWidthEdit.textEdited.connect(lambda i, v=self.widthValidate: self.onchange(i, v))
            self.maxHeightEdit.textEdited.connect(lambda i, v=self.heightValidate: self.onchange(i, v))
            self.attr2qt["max-width"] = self.maxWidthEdit
            self.attr2qt["max-height"] = self.maxHeightEdit

            mainLayout.addLayout(maxLayout)
            mainLayout.addWidget(self.hLine())

        # add widgets to show original width, height
        owidthLabel = QLabel('original width')
        oheightLabel = QLabel('original height')
        self.originalWidth = QLineEdit(self)
        self.originalHeight = QLineEdit(self)
        self.disableLineEdit(self.originalWidth)
        self.disableLineEdit(self.originalHeight)

        sizeLayout2 = QHBoxLayout()
        sizeLayout2.addWidget(owidthLabel)
        sizeLayout2.addWidget(self.originalWidth)
        sizeLayout2.addWidget(oheightLabel)
        sizeLayout2.addWidget(self.originalHeight)
        mainLayout.addLayout(sizeLayout2)

        # add Image Occlusion related buttons
        if self.is_occl:
            mainLayout.addWidget(self.hLine())
            occlLabel = QLabel("Image Occlusion")
            occlLabel.setStyleSheet("QLabel {font-weight : bold;}")            
            mainLayout.addWidget(occlLabel)
            occlAllNote = QCheckBox("Apply to all notes")
            self.occlAllNote = occlAllNote
            occlLayout = QHBoxLayout()
            occlLayout.addWidget(occlAllNote)
            self.attr2qt["Apply to all notes"] = self.occlAllNote
            if self.curr_fld in self.main.all_occl_flds:
                occlAllFld = QCheckBox("Apply to all fields")
                self.occlAllFld = occlAllFld
                occlLayout.addWidget(occlAllFld)
                self.attr2qt["Apply to all fields"] = self.occlAllFld
            mainLayout.addLayout(occlLayout)
            

        # add buttons
        okButton = QPushButton("OK")
        okButton.clicked.connect(self.clicked_ok)
        okButton.setDefault(True)
        okButton.setShortcut("Ctrl+Return")
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.clicked_cancel)
        resetButton = QPushButton("Default")
        resetButton.clicked.connect(self.clicked_defaults)

        btnLayout = QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(okButton)
        btnLayout.addWidget(cancelButton)
        btnLayout.addWidget(resetButton)
        mainLayout.addLayout(btnLayout)

        # center the window
        self.move(QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())

        self.setWindowTitle('Style Editor')
        self.show()

class Main:

    def __init__(self):
        self.prev_curr_field = None
        self.all_occl_flds = mw.addonManager.getConfig(__name__)["zzimage-occlusion-field-position"] 
        for i in range(len(self.all_occl_flds)):
            self.all_occl_flds[i] = self.all_occl_flds[i] - 1 #1-based to 0-based 
        # single quotes are auto changed to double quotes. So must be double quotes.
        self.hidden_div = """<div style="display:none !important;">HIDDEN DIV FROM IMAGE-SIZE-EDITOR</div>"""

    def fill_in(self, styles, original):
        if self.style_editor:
            self.style_editor.set_prev_styles(styles)
            self.style_editor.fill_in(styles, original)

    def open_edit_window(self, editor, name, is_occl):
        try:
            self.style_editor.close()
        except Exception:
            pass
        self.editor = editor
        self.name = name
        self.style_editor = UI(self, editor, name, is_occl, self.prev_curr_field)
        editor.saveNow(self.get_styles)

    def escape(self, s):
        s = s.replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace("'", "\\'")
        s = s.replace("`", "\\`")
        return s

    def get_occl_notes(self):
        """
        https://github.com/glutanimate/image-occlusion-enhanced/blob/ad092efa5bed559de42ac38d09069fc33c5a458f/src/image_occlusion_enhanced/add.py#L122
        https://github.com/glutanimate/image-occlusion-enhanced/blob/03071c1b25afbbcf3b990157a52cfadb959416a6/src/image_occlusion_enhanced/ngen.py#L101
        https://github.com/glutanimate/image-occlusion-enhanced/blob/03071c1b25afbbcf3b990157a52cfadb959416a6/src/image_occlusion_enhanced/ngen.py#L234
        """
        occl_id_fld_name = mw.addonManager.getConfig(__name__)["zzimage-occlusion-id-field"]
        occln_id = self.editor.note[occl_id_fld_name]
        if occln_id is None or occln_id.count("-") != 2:
            msg = "ERROR: Invalid Note, or a bug. Probably no need to restart however.\n"
            sys.stderr.write(msg)
        occl_id_grps = occln_id.split('-')
        uniq_id = occl_id_grps[0]
        occl_tp = occl_id_grps[1]
        occl_id = '%s-%s' % (uniq_id, occl_tp)
        query = "'%s':'%s*'" % (occl_id_fld_name, occl_id)
        res = mw.col.findNotes(query)
        note_arr = []
        for nid in res:
            note_arr.append(mw.col.getNote(nid))
        return note_arr
    
    def occl_web_eval(self, fldval, styles, noten, fldn):
        e = self.escape
        self.editor.web.eval("""
            try{{
                var div = document.createElement("div");
                div.innerHTML = "{}";
                styles = JSON.parse("{}")
                e = div.querySelector('img')
                for(a in styles){{
                    e.style[a] = styles[a]
                }}
                pycmd("occlReturn#{}#{}#" + div.innerHTML);
            }}catch(err){{
                pycmd("err#" + err)
            }}
        """.format(e(fldval), e(json.dumps(styles)), str(noten), str(fldn)))

    def occl_modify_styles(self, styles, all_fld, all_notes):
        if all_notes:
            self.occl_notes = self.get_occl_notes()
        else:
            self.occl_notes = [self.editor.note]
        if all_fld:
            self.occl_flds = self.all_occl_flds
        else:
            self.occl_flds = [self.prev_curr_field]

        self.occl_rep_tot = len(self.occl_notes) * len(self.occl_flds)
        self.occl_rep_cnt = 0
        for noten in range(len(self.occl_notes)): 
            for fldn in range(len(self.occl_flds)):
                note = self.occl_notes[noten]
                fld = self.occl_flds[fldn]
                fldval = note.fields[fld]
                self.occl_web_eval(fldval, styles, noten, fldn)

    def modify_styles(self, styles):
        """
            styles: string of dictionary of {name:value}
        """
        # replace if one empty input with string in user config
        empty_replacer = mw.addonManager.getConfig(__name__)["empty_means"]
        if empty_replacer:
            if styles["width"] and not styles["height"]:
                styles["height"] = empty_replacer
            elif not styles["width"] and styles["height"]:
                styles["width"] = empty_replacer

        e = self.escape
        curr_fld = self.prev_curr_field
        fldval = self.editor.note.fields[curr_fld]
        self.editor.web.eval("""
        try{{
            var div = document.createElement("div");
            div.innerHTML = "{}";
            var styles = JSON.parse("{}")
            var e = div.querySelector('img[src="{}"]')
            for(var a in styles){{
                e.style[a] = styles[a]
            }}
            pycmd("htmlReturn#" + div.innerHTML);
            div.remove()
        }}catch(err){{
            pycmd("err#" + err)
        }}
        """.format(e(fldval), e(json.dumps(styles)), e(self.name)))

    def get_styles(self):
        e = self.escape
        curr_fld = self.prev_curr_field
        fldval = self.editor.note.fields[curr_fld]
        self.editor.web.eval("""
        try{{
            var css_names = ['width','height','min-height','min-width','max-height','max-width']
            var styles = {{}};
            var div = document.createElement("div");
            div.innerHTML = `{}`;
            var e = div.querySelector('img[src="{}"]');
            returnStyling = function(){{
                if(e.complete){{
                    for(var a = 0; a < css_names.length; a++){{
                        val = e.style[css_names[a]];
                        if(val){{styles[css_names[a]] = val}}
                }}
                original = {{"height": e.naturalHeight, "width": e.naturalWidth}};
                d = {{"s":styles,"o":original}};
                d = JSON.stringify(d);
                pycmd("getImageStyle#" + d);
                div.remove();
                }}else{{
                    setTimeout(returnStyling,15);
                }}
            }}
            returnStyling();

        }}catch(err){{
            pycmd("err#" + err);
        }}
        """.format(e(fldval), e(self.name)))

    def modify_fields(self, fldval):
        editor = self.editor
        curr_fld = self.prev_curr_field
        if mw.addonManager.getConfig(__name__)["hidden-div-for-image-only-field"]:
            if self.hidden_div not in fldval:
                if re.match(r"^(?:\s|(?:<br>))*<img[^>]*>(?:\s|(?:<br>))*$", fldval):
                    fldval += self.hidden_div
        editor.note.fields[curr_fld] = fldval
        if not editor.addMode:
            editor.note.flush()
        editor.loadNote(focusTo=curr_fld)

    def occl_modify_fields(self, noten, fldn, fldval):
        try:
            config = self.style_editor.config
        except AttributeError:
            config = mw.addonManager.getConfig(__name__)

        #because of this bug in AnkiDroid. https://github.com/ankidroid/Anki-Android/issues/5166
        if config["zzimage-occlusion-hidden-div"]: 
            div = self.hidden_div
        else:
            div = ""
        if fldn == self.all_occl_flds[0]:
            if div not in fldval:
                fldval += div
        editor = self.editor
        note = self.occl_notes[noten]
        note.fields[self.occl_flds[fldn]] = fldval
        if not editor.addMode:
            note.flush()
        self.occl_rep_cnt += 1
        if self.occl_rep_cnt == self.occl_rep_tot:
            note_id = self.editor.note.id
            upd_note = mw.col.getNote(note_id)
            editor.setNote(upd_note, focusTo=self.prev_curr_field)



main = Main()


def addToContextMenu(self, m):
    context_data = self.page().contextMenuData()
    url = context_data.mediaUrl()
    image_name = url.fileName()
    occl_name = mw.addonManager.getConfig(__name__)["zzimage-occlusion-note-type"]
    is_occl = False
    if self.editor.note.model()["name"] == occl_name:
        is_occl = True
    if url.isValid() and main.prev_curr_field is not None:
        a = m.addAction("Image Styles")
        a.triggered.connect(lambda _, s=self.editor, n=image_name, o=is_occl: main.open_edit_window(s, n, o))


def onBridgeCmd(self, cmd, _old):
    if not self.note or not runHook:
        return
    if cmd.startswith("htmlReturn#"):
        cmd = cmd.replace("htmlReturn#", "")
        main.modify_fields(cmd)

    elif cmd.startswith("getImageStyle#"):
        cmd = cmd.replace("getImageStyle#", "")
        ret = json.loads(cmd)
        main.fill_in(ret["s"], ret["o"])
    elif cmd.startswith("occlReturn#"):
        cmd = cmd.replace("occlReturn#", "")
        m = re.match(r"^(\d+)#(\d+)#([\s\S]*)$", cmd)
        noten = int(m.group(1)) #If m doesn't exist, anki will raise an error.
        fldn = int(m.group(2)) 
        fldval = m.group(3)
        main.occl_modify_fields(noten, fldn, fldval)

    elif cmd.startswith("err#"):
        sys.stderr.write(cmd)
    else:
        if cmd.startswith("focus"):
            (type, num) = cmd.split(":", 1)
            main.prev_curr_field = int(num)
        return _old(self, cmd)


def onProfileLoaded():
    Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, onBridgeCmd, "around")
    if "zzz-version-checkpoint" not in mw.addonManager.getConfig(__name__): #version <= 2.1.1temppatch
        fix_occlbug()  
    else: # version >= 2.2
        return


addHook("EditorWebView.contextMenuEvent", addToContextMenu)
addHook("profileLoaded", onProfileLoaded)


def fix_occlbug():
    mw.progress.start(immediate=True, label="Please wait, this should not take long")
    nids = find_occlbug_affected_notes()
    tag_notes(nids)
    mw.progress.finish()
    if len(nids) > 0:
        showText("""
PLEASE READ THIS CAREFULLY. You will only see this message once. (You can find the text in the addon page though)

Sorry!!
There was a bug in previous version of the addon 'Image Style Editor'.
When editing image sizes in image occlusion notes, it made all the cards of the note have the same occlusion masks.
A total of %d notes were found affected by the bug, and they were tagged "image-style-occl-bugged".

To fix your notes, please do the following: 
1. Click Browse, search for "tag:image-style-occl-bugged" (without quotes)
2. For each note, remove "image-style-occl-bugged" tag, then press 'Edit Image Occlusion'(Ctrl + Shift + O) on top right. 
3. Move one of the masks by 1mm. There needs to be a change to the note.
4. Click 'Edit Cards' on the bottom.
"""%len(nids))

def find_occlbug_affected_notes():
    occl_type_name = mw.addonManager.getConfig(__name__)["zzimage-occlusion-note-type"]
    srch_term = "\"note:{}\"".format(occl_type_name) 
    res = mw.col.findNotes(srch_term)

    to_fix_nid = [] #only list 1 note of each occl_note

    occl_id_fld_name = mw.addonManager.getConfig(__name__)["zzimage-occlusion-id-field"]
    all_occl_flds = mw.addonManager.getConfig(__name__)["zzimage-occlusion-field-position"]
    all_occl_flds.pop(0) #the original image will be same regardless of bug
    all_occl_flds.pop(-1) #the original mask field will also be the same
    for i in range(len(all_occl_flds)):
        all_occl_flds[i] = all_occl_flds[i] - 1 #1-based to 0-based 
    occl_note_vals = {} #occln_id: [[fld1s,], [fld2s,], [fld3s,]...]
    for nid in res:
        note = mw.col.getNote(nid)
        occln_id = note[occl_id_fld_name]
        occl_id_grps = occln_id.split('-')
        if len(occl_id_grps) < 1: #broken note
            continue
        uniq_id = occl_id_grps[0]
        occl_tp = occl_id_grps[1]
        occln_id = uniq_id + "-" + occl_tp
        if occln_id not in occl_note_vals:
            empty_list = []
            for x in range(len(all_occl_flds)):
                empty_list.append([])
            occl_note_vals.update({occln_id : empty_list })
        for f in range(len(all_occl_flds)):
            fld = all_occl_flds[f]
            print(occl_note_vals[occln_id][f])
            print(note.fields[fld])
            occl_note_vals[occln_id][f].append(note.fields[fld])
    
    to_fix_occl_nid = []
    for note in occl_note_vals:
        if len(occl_note_vals[note][0]) == 1:
            continue
        for fld in range(len(all_occl_flds)):
            for i, e in enumerate(occl_note_vals[note][fld]):
                cnt = 0
                for j in range(i + 1, len(occl_note_vals[note][fld])):
                    if e == occl_note_vals[note][fld][j]:
                        if note not in to_fix_occl_nid:
                            to_fix_occl_nid.append(note)
        
    for occl_nid in to_fix_occl_nid:
        query = "'%s':'%s*'" % (occl_id_fld_name, occl_nid)
        res = mw.col.findNotes(query)
        note = mw.col.getNote(res[0])
        to_fix_nid.append(note.id)
    
    return to_fix_nid

def tag_notes(notes):
    TAG = "image-style-occl-bugged"
    for nid in notes:
        note = mw.col.getNote(nid)
        if TAG not in note.tags:
            note.tags.append(TAG)
        note.tags = mw.col.tags.canonify(note.tags)
        note.flush()
