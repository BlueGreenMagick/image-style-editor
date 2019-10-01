# -*- coding: utf-8 -*-

"""
Anki Add-on: Image Style Editor
"""

import os
import json
import sys

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
        self.setupUI()

    def clicked_ok(self):
        styles = {
            "width": self.widthEdit.text(),
            "height": self.heightEdit.text()
        }
        self.main.modify_styles(styles)
        self.close()

    def clicked_cancel(self):
        self.close()

    def clicked_reset(self):
        self.fill_in(self.original_styles, self.original)

    def set_original_styles(self, styles):
        self.original_styles = styles

    def fill_in(self, styles, original):
        self.original = original
        for a in styles:
            if a == "width":
                self.widthEdit.setText(styles[a])
            elif a == "height":
                self.heightEdit.setText(styles[a])

        for o in original:
            if o == "width":
                self.originalWidth.setText(str(original[o]))
            elif o == "height":
                self.originalHeight.setText(str(original[o]))

    def hLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def setupUI(self):
            # main layout
            mainLayout = QVBoxLayout()
            self.setLayout(mainLayout)

            # add widgets to set height and width
            widthLable = QLabel('width')
            heightLable = QLabel('height')
            self.widthEdit = QLineEdit(self)
            self.heightEdit = QLineEdit(self)

            sizeLayout = QHBoxLayout()
            sizeLayout.addWidget(widthLable)
            sizeLayout.addWidget(self.widthEdit)
            sizeLayout.addWidget(heightLable)
            sizeLayout.addWidget(self.heightEdit)
            mainLayout.addLayout(sizeLayout)

            # add an horizontal line
            mainLayout.addWidget(self.hLine())

            # add widgets to show original width, height
            owidthLable = QLabel('original width')
            oheightLable = QLabel('original height')
            self.originalWidth = QLineEdit(self)
            self.originalHeight = QLineEdit(self)
            self.disableLineEdit(self.originalWidth)
            self.disableLineEdit(self.originalHeight)

            sizeLayout2 = QHBoxLayout()
            sizeLayout2.addWidget(owidthLable)
            sizeLayout2.addWidget(self.originalWidth)
            sizeLayout2.addWidget(oheightLable)
            sizeLayout2.addWidget(self.originalHeight)
            mainLayout.addLayout(sizeLayout2)

            # add OK and Cancel buttons
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

    def disableLineEdit(self, lineEdit):
        lineEdit.setReadOnly(True)

        # change color
        palette = QPalette()
        palette.setColor(QPalette.Base, Qt.gray)
        lineEdit.setPalette(palette)


class Main:

    def __init__(self):
        self.lastCurrentField = None
        
    def fill_in(self, styles, original):
        if self.style_editor:
            self.style_editor.set_original_styles(styles)
            self.style_editor.fill_in(styles, original)

    def open_edit_window(self, editor, name):
        self.name = name
        self.editor = editor
        self.style_editor = UI(self, editor, name)
        editor.saveNow(self.get_styles)

    def e(self,s):
        s = s.replace('"', '\\"')
        s = s.replace("'", "\\'")
        return s

    def modify_styles(self, styles):
        """
            styles: string of dictionary of {name:value}
        """
        empty_replacer = mw.addonManager.getConfig(__name__)["empty_means"]
        if empty_replacer:
            if styles["width"] and not styles["height"]:
                styles["height"] = empty_replacer
            elif not styles["width"] and styles["height"]:
                styles["width"] = empty_replacer
        
        cur_fld = self.lastCurrentField
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
        """.format(self.e(fld),self.e(json.dumps(styles)),self.e(self.name)))

    def get_styles(self):
        cur_fld = self.lastCurrentField
        fld = self.editor.note.fields[cur_fld]
        self.editor.web.eval("""
        try{{
            css_names = ['width','height']
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
        """.format(self.e(fld),self.e(self.name)))

    def modify_fields(self, txt):
        editor = self.editor
        cur_fld = self.lastCurrentField
        editor.note.fields[cur_fld] = txt
        editor.note.flush()
        editor.loadNote(focusTo=cur_fld)
        

main = Main()

def addToContextMenu(self,m):
    context_data = self.page().contextMenuData()
    url = context_data.mediaUrl()
    image_name = url.fileName()
    if url.isValid() and main.lastCurrentField is not None: 
        a = m.addAction("Image Styles")
        a.triggered.connect(lambda _, s=self.editor, n=image_name: main.open_edit_window(s,n))

def onBridgeCmd(self, cmd, _old):
    if not self.note or not runHook:
        return
    if cmd.startswith("htmlReturn#"):
        cmd = cmd.replace("htmlReturn#", "")
        main.modify_fields(cmd)

    elif cmd.startswith("getImageStyle#"):
        cmd = cmd.replace("getImageStyle#","")
        ret = json.loads(cmd)
        main.fill_in(ret["s"], ret["o"])
    elif cmd.startswith("err#"):
        sys.stderr.write(cmd)
    else:
        if cmd.startswith("focus"):
            (type, num) = cmd.split(":", 1)
            main.lastCurrentField = int(num)
        return _old(self, cmd)

def onProfileLoaded():
    Editor.onBridgeCmd = wrap(Editor.onBridgeCmd, onBridgeCmd, "around")

addHook("EditorWebView.contextMenuEvent", addToContextMenu)
addHook("profileLoaded", onProfileLoaded)