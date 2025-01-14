#  This file is part of Qnotero.
#
#      Qnotero is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Qnotero is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Qnotero.  If not, see <https://www.gnu.org/licenses/>.
#      Copyright (c) 2019 E. Albiter

#

from libqnotero.qt.QtGui import QListWidget, QInputDialog
from libqnotero.qt.QtCore import Qt
from pathlib import Path
import subprocess
import os
import platform
import requests

# GLOBAL VARIABLES
REMARKABLE_IP = "10.11.99.1"
DOCUMENT_LIST_REQUEST = "http://{ip}/documents/{guid}"
DOCUMENT_UPLOAD_REQUEST = "http://{ip}/upload"

# FUNCTIONS FOR REMARKABLE

def select_directory(guid=""):
    global REMARKABLE_IP, DOCUMENT_LIST_REQUEST
    req_str = DOCUMENT_LIST_REQUEST.format(ip=REMARKABLE_IP, guid=guid)
    try:
        response = requests.get(req_str, timeout=5)
    except requests.exceptions.Timeout:
        return 0
    return response.status_code


def upload_file(fpath):
    global DOCUMENT_UPLOAD_REQUEST

    # Prepare request headers and files
    headers = {
        "Origin": f"http://{REMARKABLE_IP}",
        "Accept": "*/*",
        "Referer": f"http://{REMARKABLE_IP}/",
        "Connection": "keep-alive",
    }
    files = {
        "file": (fpath.name, fpath.open("rb"), "application/pdf"),
    }

    # Send request

    response = requests.post(
        DOCUMENT_UPLOAD_REQUEST.format(ip=REMARKABLE_IP), headers=headers, files=files
    )

    return response

def send_to_remarkable(fpath):
    # if not pdf >> pass
    if fpath.suffix != ".pdf":
        msg = f"[Send to RK] Bad file extension for {fpath.name}: \n transfer only works for pdf files."
        zenity_notif(msg)
        return

    # check remarkable
    if select_directory() != 200:
        msg = f"[Send to RK] Cannot connect to Remarkable. \n Check that it is accessible at http://{REMARKABLE_IP}"
        zenity_notif(msg)
        return

    # upload
    response = upload_file(fpath)
    if response.status_code == 201:
        msg = f"[Send to RK] {fpath.name} uploaded to Remarkable !"
        zenity_notif(msg)
    else:
        msg = f"[Send to RK] ERROR Uploading {fpath.name} : (status {response.status_code})!"
        zenity_notif(msg)
    return

def zenity_notif(msg=""):
    try:
        r = subprocess.run(["zenity", "--notification", "--text", msg])
    except:
        pass

# ----------------------------------------------------------

class QnoteroResults(QListWidget):
    """The Qnotero result list"""

    def __init__(self, qnotero):

        """
		Constructor

		Arguments:
		qnotero -- a Qnotero instance
		"""

        QListWidget.__init__(self, qnotero)
        self.itemDoubleClicked.connect(self.DoubleClicked)
        self.itemClicked.connect(self.Clicked)
        self.setMouseTracking(True)


    def _attached_files_path(self, fpath):
        """
        A. DAREAU - QUICKFIX
        attached files have a path starting with "attachments:"
        this function parses the name and return a correct path
        /!\ the path is hard coded for my config...
        """
        if fpath.startswith('attachments:'):
            home = os.path.expanduser('~')
            attachement_root = os.path.join(home, 'Biblio', 'Articles')
            fpath = fpath.replace('attachments:', '')
            fpath = os.path.join(attachement_root, fpath)
        return fpath


    def DoubleClicked(self, item):

        """
		Open file attachment or URL

		Arguments:
		item -- a qnoteroItem
		"""

        if item is None or not hasattr(item, "zoteroItem"):
            return
        zoteroItem = item.zoteroItem
        if zoteroItem.fulltext is None and zoteroItem.url is None:
            print('qnoteroResults.mousePressEvent(): no file attachment nor url')
            return
        # If there is no a fulltext item open the URL of the entry
        if len(zoteroItem.fulltext) == 0:
            path = zoteroItem.url
        # Only one attachment
        elif len(zoteroItem.fulltext) == 1:
            path = zoteroItem.fulltext[0]
        # If there are more than one
        else:
            path, okPressed = QInputDialog.getItem(self, u'Attachments',
                                                   u'Select attachment to open:', zoteroItem.fulltext, 0, False)
            if path is None or not okPressed:
                return

        print("qnoteroResults.DoubleClicked(): prepare to open %s"
              % path)
        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':  # Windows
                path = os.path.normpath(path)
                os.startfile(path)
            else:  # linux variants
                # QUICKFIX (A. Dareau) ----------------------------------------
                # for some reason, the "fulltext" attribute starts
                # with 'attachments:', followed by the path relative to the
                # current user home folder (in my case at least). I fix
                # that by replacing 'attachments:' by the current user home
                path = self._attached_files_path(path)
                # --------------------------------------------------------------
                subprocess.call(('xdg-open', path))
            print("qnoteroResults.DoubleClicked(): file opened")
        except Exception as exc:
            print("qnoteroResults.DoubleClicked(): failed to open file or URL, sorry... %s" % exc)

        self.qnotero.popDown()


    def keyPressEvent(self, e):

        """
		Handle key presses

		Arguments:
		e -- a QKeyEvent
		"""

        if (e.key() == Qt.Key_Up and self.currentRow() == 0) \
                or (e.key() == Qt.Key_F and Qt.ControlModifier & e.modifiers()):
            self.qnotero.ui.lineEditQuery.selectAll()
            self.qnotero.ui.lineEditQuery.setFocus()
            return
        # AD : pressing 'Enter' opens the item
        elif (e.key() == Qt.Key_Return):
            item = self.currentItem()
            self.DoubleClicked(item)
            return

        # AD : pressing 'x' opens the item with xournalpp
        elif (e.key() == Qt.Key_X):
            item = self.currentItem()
            self.OpenXournalpp(item)
            return

        # AD : pressing 'm' starts writing an email with the pdf attached
        elif (e.key() == Qt.Key_M):
            item = self.currentItem()
            self.SendByMail(item)
            return

        # AD : pressing 'r' transfers to remarkable
        elif (e.key() == Qt.Key_R):
            item = self.currentItem()
            self.SendToRemarkable(item)
            return
        
        QListWidget.keyPressEvent(self, e)


    def OpenXournalpp(self, item):
        """
        Open file in xournalpp

        Arguments:
        item -- a qnoteroItem
        """
        #TODO : refactor with DoubleClicked()

        if item is None or not hasattr(item, "zoteroItem"):
            return
        zoteroItem = item.zoteroItem
        if zoteroItem.fulltext is None and zoteroItem.url is None:
            return
        # If there is no a fulltext item : return
        if len(zoteroItem.fulltext) == 0:
            return
        # Only one attachment
        elif len(zoteroItem.fulltext) == 1:
            path = zoteroItem.fulltext[0]
        # If there are more than one
        else:
            path, okPressed = QInputDialog.getItem(self, u'Attachments',
                                                   u'Select attachment to open:', zoteroItem.fulltext, 0, False)
            if path is None or not okPressed:
                return

        print("qnoteroResults.OpenXournalpp(): prepare to open %s"
              % path)
        try:
            if platform.system() == 'Darwin':  # macOS
                pass
            elif platform.system() == 'Windows':  # Windows
                pass
            else:  # linux variants
                path = self._attached_files_path(path)
                # if there is already a xournal file : open it
                if os.path.isfile(path + '.xopp'):
                    subprocess.Popen(['/usr/bin/xournalpp', path + '.xopp'])
                else:
                    subprocess.Popen(['/usr/bin/xournalpp', path])
            print("qnoteroResults.OpenXournalpp(): file opened")
        except Exception as exc:
            print("qnoteroResults.OpenXournalpp(): failed to open file, sorry... %s" % exc)

        self.qnotero.popDown()

    def SendByMail(self, item):
        """
        Start writing an email with the pdf attached

        Arguments:
        item -- a qnoteroItem
        """
        #TODO : refactor with DoubleClicked()

        if item is None or not hasattr(item, "zoteroItem"):
            return
        zoteroItem = item.zoteroItem
        if zoteroItem.fulltext is None and zoteroItem.url is None:
            return
        # If there is no a fulltext item : return
        if len(zoteroItem.fulltext) == 0:
            return
        # Only one attachment
        elif len(zoteroItem.fulltext) == 1:
            path = zoteroItem.fulltext[0]
        # If there are more than one
        else:
            path, okPressed = QInputDialog.getItem(self, u'Attachments',
                                                   u'Select attachment to open:', zoteroItem.fulltext, 0, False)
            if path is None or not okPressed:
                return

        print("qnoteroResults.SendByMail(): prepare email %s"
              % path)
        try:
            if platform.system() == 'Darwin':  # macOS
                pass
            elif platform.system() == 'Windows':  # Windows
                pass
            else:  # linux variants
                path = self._attached_files_path(path)
                # if there is already a xournal file : open it
                subprocess.Popen(['/usr/bin/xdg-email',
                                  '--subject', zoteroItem.title,
                                  '--attach', path])
            print("qnoteroResults.OpenXournalpp(): file opened")
        except Exception as exc:
            print("qnoteroResults.OpenXournalpp(): failed to open file, sorry... %s" % exc)
        self.qnotero.popDown()


    def SendToRemarkable(self, item):
        """
        Transfers the item to remarkable via local webserver
        https://remarkable.guide/tech/usb-web-interface.html#api

        Arguments:
        item -- a qnoteroItem
        """
        #TODO : refactor with DoubleClicked()
        if item is None or not hasattr(item, "zoteroItem"):
            return
        zoteroItem = item.zoteroItem
        if zoteroItem.fulltext is None and zoteroItem.url is None:
            return
        # If there is no a fulltext item open the URL of the entry
        if len(zoteroItem.fulltext) == 0:
            path = zoteroItem.url
        # Only one attachment
        elif len(zoteroItem.fulltext) == 1:
            path = zoteroItem.fulltext[0]
        # If there are more than one
        else:
            path, okPressed = QInputDialog.getItem(self, u'Attachments',
                                                   u'Select attachment to open:', zoteroItem.fulltext, 0, False)
            if path is None or not okPressed:
                return

        try:
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', path))
            elif platform.system() == 'Windows':  # Windows
                path = os.path.normpath(path)
                os.startfile(path)
            else:  # linux variants
                # QUICKFIX (A. Dareau) ----------------------------------------
                # for some reason, the "fulltext" attribute starts
                # with 'attachments:', followed by the path relative to the
                # current user home folder (in my case at least). I fix
                # that by replacing 'attachments:' by the current user home
                path = self._attached_files_path(path)
                # --------------------------------------------------------------
                fpath = Path(path)
                send_to_remarkable(fpath)
            print("qnoteroResults.DoubleClicked(): file opened")
        except Exception as exc:
            print("qnoteroResults.DoubleClicked(): failed to open file or URL, sorry... %s" % exc)

        self.qnotero.popDown()


    def Clicked(self, item):
        if item is None or not hasattr(item, "zoteroItem"):
            return
        zoteroItem = item.zoteroItem
        self.qnotero.ui.textAbstract.setText(zoteroItem.abstract)
