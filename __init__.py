"""
Anki Add-on: Image Style Editor
"""

import os
import json
import sys
import re

from aqt import mw
from aqt.editor import EditorWebView, Editor
from aqt.qt import *
from anki.hooks import addHook, runHook, wrap


class UI(QWidget):

    def __init__(self, main, editor, img_name):
        super(UI, self).__init__()
        self.editor = editor
        self.image_name = img_name
        self.main = main
        self.config = mw.addonManager.getConfig(__name__)
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
        self.main.modify_styles(styles)
        self.close()

    def clicked_cancel(self):
        self.close()

    def clicked_reset(self):
        self.fill_in(self.prev_styles, self.original)

    def set_prev_styles(self, styles):
        self.prev_styles = styles

    def fill_in(self, styles, original):
        self.original = original
        for a in styles:
            val = styles[a]
            if a == "width":
                self.widthEdit.setText(val)
            elif a == "height":
                self.heightEdit.setText(val)
            else:
                if self.config["min-size"]:
                    if a == "min-width":
                        self.minWidthEdit.setText(val)
                    elif a == "min-height":
                        self.minHeightEdit.setText(val)
                if self.config["max-size"]:
                    if a == "max-width":
                        self.maxWidthEdit.setText(val)
                    elif a == "max-height":
                        self.maxHeightEdit.setText(val)

        for o in original:
            if o == "width":
                self.originalWidth.setText(str(original[o]) + "px")
            elif o == "height":
                self.originalHeight.setText(str(original[o]) + "px")

    def check_valid_input(self, inp):
        valids = ["", "auto", "inherit", "initial", "unset"]
        valid_re = r"^\d+(?:\.\d+)?(?:px|cm|mm|in|pc|pt|ch|em|ex|rem|%|vw|vh|vmin|vmax)?$|^(?:var|calc|attr)\([\s\S]*\)$"
        if inp in valids:
            return True
        elif re.match(valid_re, inp) is not None:
            return True
        else:
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

        # add buttons
        okButton = QPushButton("OK")
        okButton.clicked.connect(self.clicked_ok)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.clicked_cancel)
        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self.clicked_reset)

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

    def fill_in(self, styles, original):
        if self.style_editor:
            self.style_editor.set_prev_styles(styles)
            self.style_editor.fill_in(styles, original)

    def open_edit_window(self, editor, name):
        self.editor = editor
        self.name = name
        self.style_editor = UI(self, editor, name)
        editor.saveNow(self.get_styles)

    def escape(self, s):
        s = s.replace('"', '\\"')
        s = s.replace("'", "\\'")
        return s

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
        cur_fld = self.prev_curr_field
        fld = self.editor.note.fields[cur_fld]
        self.editor.web.eval("""
        try{{
            var div = document.createElement("div");
            div.innerHTML = "{}";
            styles = JSON.parse("{}")
            e = div.querySelector('img[src="{}"]')
            for(a in styles){{
                e.style[a] = styles[a]
            }}
            pycmd("htmlReturn#" + div.innerHTML);
        }}catch(err){{
            pycmd("err#" + err)
        }}
        """.format(e(fld), e(json.dumps(styles)), e(self.name)))

    def get_styles(self):
        e = self.escape
        cur_fld = self.prev_curr_field
        fld = self.editor.note.fields[cur_fld]
        self.editor.web.eval("""
        try{{
            css_names = ['width','height','min-height','min-width','max-height','max-width']
            styles = {{}}
            var div = document.createElement("div");
            div.innerHTML = "{}"
            e = div.querySelector('img[src="{}"]')
            for(a = 0; a < css_names.length; a++){{
                val = e.style[css_names[a]]
                if(val){{styles[css_names[a]] = val}}
            }}
            original = {{"height": e.naturalHeight, "width": e.naturalWidth}}
            d = {{"s":styles,"o":original}}
            d = JSON.stringify(d)
            pycmd("getImageStyle#" + d)
        }}catch(err){{
            pycmd("err#" + err);
        }}
        """.format(e(fld), e(self.name)))

    def modify_fields(self, txt):
        editor = self.editor
        cur_fld = self.prev_curr_field
        editor.note.fields[cur_fld] = txt
        editor.note.flush()
        editor.loadNote(focusTo=cur_fld)


main = Main()


def addToContextMenu(self, m):
    context_data = self.page().contextMenuData()
    url = context_data.mediaUrl()
    image_name = url.fileName()
    if url.isValid() and main.prev_curr_field is not None:
        a = m.addAction("Image Styles")
        a.triggered.connect(lambda _, s=self.editor, n=image_name: main.open_edit_window(s, n))


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
    elif cmd.startswith("err#"):
        sys.stderr.write(cmd)
    else:
        if cmd.startswith("focus"):
            (type, num) = cmd.split(":", 1)
            main.prev_curr_field = int(num)
        return _old(self, cmd)


def onProfileLoaded():
    Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, onBridgeCmd, "around")


addHook("EditorWebView.contextMenuEvent", addToContextMenu)
addHook("profileLoaded", onProfileLoaded)
