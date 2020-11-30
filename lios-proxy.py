#!/usr/bin/python3
#
import os, sys
import gettext
import locale
import gi
import configparser
import random

locale.setlocale(locale.LC_ALL, '')
_ = gettext.gettext

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

proadd = _("Add Profile")

#            fdialog = Gtk.FileChooserDialog(_("Please select an image"), self,
#                    Gtk.FileChooserAction.OPEN,
#                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
#        resp = fdialog.run()
#        if resp == Gtk.ResponseType.OK:
#            iconfile = fdialog.get_filename()
#        else:
#            iconfile = "./user-1.png"

def ErrorMesg(msg):
    win = Gtk.Window()
    md = Gtk.MessageDialog(parent=win, type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, message_format=msg)
    md.show()
    md.run()
    md.destroy()
    win.destroy()

class ConProfile(Gtk.Dialog):
    def __init__(self):
        self.win = Gtk.Window()
        super().__init__(parent=win)
        self.set_title(_("Add New Profile"))
        self.set_default_size(400, 300)
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.set_default_response(Gtk.ResponseType.OK)
        self.connect("response", self.on_response)
        self.response = Gtk.ResponseType.CANCEL
        self.sec = ''
        self.profile = {}

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.add(hbox)
        label = Gtk.Label(_("   Profile ID:"))
        hbox.add(label)
        label.show()
        self.id = Gtk.Entry()
        self.id.set_max_length(36)
        hbox.pack_start(self.id, True, True, 0)
        self.id.show()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 15)
        label = Gtk.Label(_("     Protocol:"))
        hbox.add(label)
        label.show()
        rbtn1 = Gtk.RadioButton(label=_("SPICE"))
        rbtn1.connect("toggled", self.radio_on_selected)
        hbox.pack_start(rbtn1, True, True, 20)
        rbtn1.show()
        rbtn2 = Gtk.RadioButton(label=_("RDP"), group=rbtn1)
        rbtn2.connect("toggled", self.radio_on_selected)
        hbox.pack_start(rbtn2, True, True, 0)
        rbtn2.show()
        self.profile['proto'] = rbtn1.get_label()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_(" Remote IP:"))
        hbox.add(label)
        label.show()
        self.ip = Gtk.Entry()
        self.ip.set_max_length(36)
        hbox.pack_start(self.ip, True, True, 0)
        self.ip.show()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_("User Name:"))
        hbox.add(label)
        label.show()
        self.user = Gtk.Entry()
        self.user.set_max_length(36)
        hbox.pack_start(self.user, True, True, 0)
        self.user.show()

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.CANCEL:
            return

        self.sec = self.id.get_text()
        self.profile['ip'] = self.ip.get_text()
        self.profile['user'] = self.user.get_text()
        self.profile['picture'] = "./user-" + str(random.randint(1,4)) + ".png"

    def radio_on_selected(self, rbtn):
        if rbtn.get_active():
            self.profile['proto'] = rbtn.get_label()

    def destroy(self):
        super().destroy()
        self.win.destroy()
        
class LIcon(Gtk.EventBox):
    def __init__(self, sec, profile):
        super().__init__()
        self.sec = sec
        self.profile = profile
        self.connect("button-press-event", self.on_event_press)
        vbox = Gtk.VBox()
        vbox.set_homogeneous(False)
        self.add(vbox)
        vbox.show()

        image = Gtk.Image()
        image.set_from_file(profile['picture'])
        vbox.pack_start(image, False, False, 0)
        image.show()
        label = Gtk.Label(label=self.sec)
        vbox.pack_end(label, False, False, 0)
        label.show()

    def on_event_press(self, ebox, event):
        if self.sec == proadd:
            condial = ConProfile()
            condial.show()
            response = condial.run()
            condial.destroy()
            errmsg = ''
            if response == Gtk.ResponseType.OK:
                if len(condial.sec) == 0:
                    errmsg = _("Missing Profile ID")
                elif len(condial.profile['user']) == 0:
                    errmsg = _("Missing User Name")
                elif len(condial.profile['ip']) == 0:
                    errmsg = _("Missing Remote Host/IP")
                if len(errmsg) != 0:
                    ErrorMesg(errmsg)
                    return
                
                print("Section: {}".format(condial.sec))
                print(condial.profile)
        else:
            print("Will initiate a connection")

class MWin(Gtk.Window):
    def __init__(self, conini):
        super().__init__(title=_("Connection Profiles"))
        self.conini = conini;

        vbox = Gtk.VBox()
        vbox.set_homogeneous(False)
        self.add(vbox)
        vbox.show()

        self.hbox = Gtk.Box()
        self.hbox.set_homogeneous(False)
        vbox.pack_start(self.hbox, False, False, 0)
        self.hbox.show()
        
        icon = LIcon(proadd, {'picture': "./512px-New_user_icon-01.png"})
        self.hbox.pack_start(icon, False, False, 8)
        icon.show()

        for sec in self.conini.sections():
            icon = LIcon(self.conini, self.conini[sec])
            self.hbox.pack_start(icon, False, False, 8)
            icon.show()
            self.icons.append(icon)

        hbox = Gtk.Box()
        hbox.set_homogeneous(True)
        vbox.pack_end(hbox, False, False, 0)
        hbox.show()

        self.rebbut = Gtk.Button(label=_("Reboot"))
        self.rebbut.connect("clicked", self.on_button_clicked)
        hbox.pack_start(self.rebbut, True, True, 0)
        self.rebbut.show()

        self.shutbut = Gtk.Button(label=_("Shutdown"))
        self.shutbut.connect("clicked", self.on_button_clicked)
        hbox.pack_end(self.shutbut, True, True, 0)
        self.shutbut.show()


    def on_button_clicked(self, widget):
        if widget == self.rebbut:
            act = "--reboot"
        elif widget == self.shutbut:
            act = "--shutdown"
        else:
            return
        Gtk.main_quit()

if len(sys.argv) > 1:
    confile = sys.argv[1]
else:
    confile = os.environ['HOME'] + '/connections.ini'

conini = configparser.ConfigParser()
if os.path.isfile(confile):
    conini.read(confile)

win = MWin(conini)
win.connect("destroy", Gtk.main_quit)
win.resize(800, 300)
win.show()
Gtk.main()