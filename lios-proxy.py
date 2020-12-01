#!/usr/bin/python3
#
import os, sys
import gettext
import locale
import gi
import configparser
import random
import subprocess
import signal
import time
import threading

locale.setlocale(locale.LC_ALL, '')
_ = gettext.gettext

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

children = []
def child_exited(sig, frame):
    terminated = []
    if sig != signal.SIGCHLD:
        return
    for child in children:
        retv = child.poll()
        if retv:
            terminated.append(child)
    for child in terminated:
        children.remove(child)

signal.signal(signal.SIGCHLD, child_exited)

proto_cmd = {'RDP': 'xfreerdp', 'SPICE':None}
proadd = _("Add Profile")

def DialogPassword():
    win = Gtk.Window()
    md = Gtk.Dialog(win, title=_("Please Input Password"), transient_for=win, flags=0)
    md.add_buttons(
             Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
             )
    md.resize(400, 50)
    okButton = md.get_widget_for_response(response_id=Gtk.ResponseType.OK)
    okButton.set_can_default(True)
    okButton.grab_default()
    passwd = Gtk.Entry()
    box = md.get_content_area()
    box.add(passwd)
    passwd.show()
    passwd.set_visibility(False)
    passwd.set_activates_default(True)
    response = md.run()
    if response == Gtk.ResponseType.OK:
        pwdstr = passwd.get_text()
    else:
        pwdstr = None
    md.destroy()
    win.destroy()
    return pwdstr

def remote_connect(profile):
    if profile['proto'] != "RDP":
        errmsg = _("Protocol ") + self.profile['proto'] + _(" Not Implemented")
        ErrorMesg(errmsg)
        return
    proto = profile['proto']
    cmd = proto_cmd[proto]
    cmdlist = []
    cmdlist.append(cmd)
    remote = "/v:"+profile['ip']+":"+profile['port']
    cmdlist.append(remote)
    user = "/u:"+profile['user']
    cmdlist.append(user)
    for itm in profile['optarg'].split():
        cmdlist.append(itm)
    passwd = DialogPassword()
    if passwd == None:
        return
    print(cmdlist)
    passwd += '\n'
    log = open(profile['logfile'], 'w+')
    conpro = subprocess.Popen(cmdlist, stdin=subprocess.PIPE, stdout=log, stderr=log,
            start_new_session=True)
    conpro.stdin.write(passwd.encode('utf-8'))
    try:
        retv = conpro.communicate(None, timeout=0.5)
    except subprocess.TimeoutExpired:
        children.append(conpro)
        conpro.stdin.close()
    log.close()

def ErrorMesg(msg):
    win = Gtk.Window()
    md = Gtk.MessageDialog(parent=win, type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK, message_format=msg)
    md.show()
    md.run()
    md.destroy()
    win.destroy()

class ConProfile(Gtk.Dialog):
    def __init__(self, sec, profile):
        self.win = Gtk.Window()
        super().__init__(parent=win)
        self.set_title(_("Add New Profile"))
        self.add_button(_("_OK"), Gtk.ResponseType.OK)
        self.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
        self.set_default_response(Gtk.ResponseType.OK)
        self.connect("response", self.on_response)
        self.response = Gtk.ResponseType.CANCEL
        self.sec = ''
        self.profile = profile

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.add(hbox)
        label = Gtk.Label(_("   Profile ID:"))
        hbox.add(label)
        label.show()
        self.id = Gtk.Entry()
        self.id.set_text(sec)
        self.id.set_max_length(48)
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

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_(" Remote IP:"))
        hbox.add(label)
        label.show()
        self.ip = Gtk.Entry()
        try:
            ipaddr = profile['ip']
        except:
            ipaddr = ''
        self.ip.set_text(ipaddr)
        hbox.pack_start(self.ip, True, True, 0)
        self.ip.show()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_("           Port:"))
        hbox.add(label)
        label.show()
        self.port = Gtk.Entry()
        try:
            port = profile['port']
        except:
            if profile['proto'] == "SPICE":
                port = "5900"
            elif profile['proto'] == "RD":
                port = "3389"
        self.port.set_text(port)
        hbox.pack_start(self.port, True, True, 0)
        self.port.show()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_("User Name:"))
        hbox.add(label)
        label.show()
        self.user = Gtk.Entry()
        try:
            username = profile['user']
        except:
            username = ''
        self.user.set_text(username)
        hbox.pack_start(self.user, True, True, 0)
        self.user.show()

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_("option arg:"))
        hbox.add(label)
        label.show()
        self.optarg = Gtk.Entry()
        try:
            optarg = profile['optarg']
        except:
            optarg = ''
        self.optarg.set_text(optarg)
        hbox.pack_start(self.optarg, True, True, 0)
        self.optarg.show()

        proto = profile['proto']
        if proto == "SPICE":
            rbtn1.set_active(True)
        elif proto == "RDP":
            rbtn2.set_active(True)

        hbox = Gtk.Box()
        hbox.set_homogeneous(False)
        hbox.show()
        self.vbox.pack_start(hbox, False, False, 5)
        label = Gtk.Label(_("      log file:"))
        hbox.add(label)
        label.show()
        self.log = Gtk.Entry()
        try:
            logfile = profile['logfile']
        except:
            logfile = '/tmp/connections.log'
        self.log.set_text(logfile)
        hbox.pack_start(self.log, True, True, 0)
        self.log.show()

    def on_response(self, dialog, response):
        if response == Gtk.ResponseType.CANCEL:
            return

        self.sec = self.id.get_text()
        self.profile['ip'] = self.ip.get_text()
        self.profile['user'] = self.user.get_text()
        self.profile['port'] = self.port.get_text()
        self.profile['optarg'] = self.optarg.get_text()
        self.profile['picture'] = "./user-" + str(random.randint(1,4)) + ".png"
        self.profile['logfile'] = self.log.get_text()

    def radio_on_selected(self, rbtn):
        if rbtn.get_active():
            self.profile['proto'] = rbtn.get_label()

    def destroy(self):
        super().destroy()
        self.win.destroy()
        
class LIcon(Gtk.EventBox):
    def __init__(self, win, sec):
        super().__init__()
        self.mwin = win
        self.sec = sec
        if sec != proadd:
            self.profile = win.conini[sec]
        else:
            self.profile = win.conini['DEFAULT']
        self.connect("button-press-event", self.on_event_press)
        vbox = Gtk.VBox()
        vbox.set_homogeneous(False)
        self.add(vbox)
        vbox.show()

        image = Gtk.Image()
        image.set_from_file(self.profile['picture'])
        vbox.pack_start(image, False, False, 0)
        image.show()
        self.label = Gtk.Label(label=self.sec)
        vbox.pack_end(self.label, False, False, 0)
        self.label.show()

    def refresh_label(self):
        self.label.set_text(self.sec)

    def on_event_press(self, ebox, event):
        if self.sec == proadd:
            condial = ConProfile('def', self.profile)
            condial.resize(600, 400)
            condial.show()
            response = condial.run()
            condial.destroy()
            if event.button == 1:
                errmsg = ''
                if response == Gtk.ResponseType.OK:
                    if len(condial.sec) == 0:
                        errmsg = _("Missing Profile ID")
                    elif condial.sec.upper() == 'DEFAULT':
                        errmsg = _("Profile Name Cannot be set to 'DEFAULT'")
                    elif len(condial.profile['user']) == 0:
                        errmsg = _("Missing User Name")
                    elif len(condial.profile['ip']) == 0:
                        errmsg = _("Missing Remote Host/IP")
                    elif condial.sec in self.mwin.conini.sections():
                        errmsg = _("Duplicate Profile Name")
                    if len(errmsg) != 0:
                        ErrorMesg(errmsg)
                        return
                
                    GLib.idle_add(self.mwin.add_icon, condial.sec, condial.profile)
                    self.mwin.conmod = 1
            elif event.button == 3:
                if response == Gtk.ResponseType.OK:
                    for key in condial.profile.keys():
                        self.mwin.conini['DEFAULT'][key] = condial.profile[key]
                    self.mwin.conmod = 1
        else:
            if event.button == 1:
                remote_connect(self.profile)
            else:
                condial = ConProfile(self.sec, self.profile)
                condial.resize(600, 400)
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
                
                    if condial.sec != self.sec:
                        self.mwin.conini[condial.sec] = {}
                    for key in condial.profile.keys():
                        self.mwin.conini[condial.sec][key] = condial.profile[key]
                    if condial.sec != self.sec:
                        self.mwin.conini.remove_section(self.sec)
                        self.sec = condial.sec
                        self.profile = self.mwin.conini[self.sec]
                        self.refresh_label()
                    self.mwin.conmod = 1

class MWin(Gtk.Window):
    def __init__(self, conini):
        super().__init__(title=_("Connection Profiles"))
        self.conini = conini;
        self.conmod = 0

        vbox = Gtk.VBox()
        vbox.set_homogeneous(False)
        self.add(vbox)
        vbox.show()

        self.hbox = Gtk.Box()
        self.hbox.set_homogeneous(False)
        vbox.pack_start(self.hbox, False, False, 0)
        self.hbox.show()
        
        try:
            pic = self.conini['DEFAULT']['picture']
        except:
            self.conini['DEFAULT']['picture'] = '512px-New_user_icon-01.png'
            self.conini['DEFAULT']['proto'] = 'SPICE'
            self.conini['DEFAULT']['port'] = '5900'
            self.conmod = 1
        icon = LIcon(self, proadd)
        self.hbox.pack_start(icon, False, False, 8)
        icon.show()

        for sec in self.conini.sections():
            icon = LIcon(self, sec)
            self.hbox.pack_start(icon, False, False, 8)
            icon.show()

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

    def add_icon(self, sec, profile):
        self.conini[sec] = profile
        icon = LIcon(self, sec)
        self.hbox.pack_start(icon, False, False, 8)
        icon.show()

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

class UIThread(threading.Thread):
    def __init__(self, win):
        self.win = win
        super().__init__(target=Gtk.main)
        win.connect("destroy", Gtk.main_quit)
        win.resize(800, 300)
        win.show()

win = MWin(conini)

ui = UIThread(win)
ui.start()

alv = ui.is_alive()
while alv:
    time.sleep(1)
    alv = ui.is_alive()
ui.join()

if win.conmod != 0:
    with open(confile, 'w') as inif:
        conini['DEFAULT']['picture'] = '512px-New_user_icon-01.png'
        conini.write(inif)

sys.exit(0)
