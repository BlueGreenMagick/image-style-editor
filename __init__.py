# -*- coding: utf-8 -*-

"""
Anki Add-on: Image Attribute Editor
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
        attrs = {
            "width": self.widthEdit.text(),
            "height": self.heightEdit.text()
        }
        self.main.modify_attributes(attrs)
        self.close()

    def clicked_cancel(self):
        self.close()

    def clicked_reset(self):
        self.fill_in(self.original_attrs, self.styles)

    def set_original_attrs(self, attrs):
        self.original_attrs = attrs

    def fill_in(self, attrs, styles):
        self.styles = styles
        for a in attrs:
            if a == "width":
                self.widthEdit.setText(attrs[a])
            elif a == "height":
                self.heightEdit.setText(attrs[a])

        for s in styles:
            if s == "width":
                self.stylewidth.setText(styles[s])
            elif s == "height":
                self.styleheight.setText(styles[s])

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

            # add styles
            swidthLable = QLabel('width')
            sheightLable = QLabel('height')
            self.stylewidth = QLineEdit(self)
            self.styleheight = QLineEdit(self)
            self.disableLineEdit(self.stylewidth)
            self.disableLineEdit(self.styleheight)

            ssizeLayout = QHBoxLayout()
            ssizeLayout.addWidget(swidthLable)
            ssizeLayout.addWidget(self.stylewidth)
            ssizeLayout.addWidget(sheightLable)
            ssizeLayout.addWidget(self.styleheight)
            mainLayout.addLayout(ssizeLayout)
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

            self.setWindowTitle('Attribute Editor')
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
        
    def fill_in(self, attrs, styles):
        if self.attr_editor:
            self.attr_editor.set_original_attrs(attrs)
            self.attr_editor.fill_in(attrs, styles)

    def open_edit_window(self, editor, name):
        self.name = name
        self.editor = editor
        self.attr_editor = UI(self, editor, name)
        editor.saveNow(self.get_attributes)

    def e(self,s):
        s = s.replace('"', '\\"')
        s = s.replace("'", "\\'")
        return s

    def modify_attributes(self, attrs):
        """
            attrs: string of dictionary of {name:value}
        """
        cur_fld = self.lastCurrentField
        fld = self.editor.note.fields[cur_fld]
        self.editor.web.eval("""
        try{{
            var div = document.createElement("div");
            div.setAttribute("id","temp");
            div.innerHTML = "{}";
            document.body.appendChild(div);
            attrs = JSON.parse("{}")
            elems = document.querySelectorAll('div#temp img[src="{}"]')
            for(x = 0; x < elems.length; x++){{
                e = elems[x]
                for(a in attrs){{
                    e.setAttribute(a,attrs[a])
                }}
            }}
            pycmd("attributeReturn#" + div.innerHTML);
            document.body.removeChild(div);
        }}catch(err){{
            pycmd("err#" + err)
        }}
        """.format(self.e(fld),self.e(json.dumps(attrs)),self.e(self.name)))

    def get_attributes(self):
        cur_fld = self.lastCurrentField
        fld = self.editor.note.fields[cur_fld]
        self.editor.web.eval("""
        try{{
            attrs = ['width','height']
            st = ['width','height']
            ret = {{}}
            ret2 = {{}}
            var div = document.createElement("div");
            div.setAttribute("id","temp");
            div.innerHTML = "{}"
            document.body.appendChild(div);
            e = document.querySelector('div#temp img[src="{}"]')
            style = getComputedStyle(e)
            for(a = 0; a < attrs.length; a++){{
                val = e.getAttribute(attrs[a])
                if(val){{ret[attrs[a]] = val}}
            }}
            for(a = 0; a < st.length; a++){{
                val = style[attrs[a]]
                if(val){{ret2[attrs[a]] = val}}
            }}
            rret = {{"a":ret,"s":ret2}}
            rret = JSON.stringify(rret)
            pycmd("getImageAttribute#" + rret)
            document.body.removeChild(div);
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
    path = os.path.join(mw.col.media.dir(), image_name)
    if url.isValid() and path and main.lastCurrentField: 
        a = m.addAction("Image Attribute")
        a.triggered.connect(lambda _, s=self.editor, n=image_name: main.open_edit_window(s,n))

def onBridgeCmd(self, cmd, _old):
    if not self.note or not runHook:
        return
    if cmd.startswith("attributeReturn#"):
        cmd = cmd.replace("attributeReturn#", "")
        main.modify_fields(cmd)

    elif cmd.startswith("getImageAttribute#"):
        cmd = cmd.replace("getImageAttribute#","")
        attr = json.loads(cmd)
        main.fill_in(attr["a"], attr["s"])
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