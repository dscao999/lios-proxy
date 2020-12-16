#!/usr/bin/python3
#
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title='GMouse 600')
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.background = Gtk.Image.new_from_file('./lios-proxy-background-1920x1080.png')
        self.overlay.add(self.background)
        self.grid = Gtk.Grid()
        self.button = Gtk.Button(label='Test')
        self.grid.add(self.button)
        self.overlay.add_overlay(self.grid)

window = MainWindow()
window.connect('delete-event', Gtk.main_quit)
window.show_all()
Gtk.main()
