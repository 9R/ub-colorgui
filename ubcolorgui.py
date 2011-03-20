#!/usr/bin/python

import gtk
import sys
import uberbus.moodlamp
import dbus, gobject, avahi
from dbus.mainloop.glib import DBusGMainLoop

TYPE="_moodlaml._udp"
#TODO: Text input for fadetime
t = 0.5
icon = "/usr/share/ub-colorgui/ml_icon.png"
#TODO: Autodetect lamps using avahi
lamps = ["alle.local", "moon.local", "spot.local", "oben.local", "unten.local"]


class UBColorGui:
    def __init__(self):
        window = gtk.Window()
        vbox1 = gtk.VBox()
        hbox1 = gtk.HBox()
        window.add(vbox1)
        window.connect("delete_event", gtk.main_quit)
        window.set_border_width(5)
        window.set_icon_from_file(icon)
        color = gtk.ColorSelection()
        color.connect("color_changed",self.new_color)
        combobox = gtk.combo_box_new_text()
        combobox.set_border_width(5)
        label = gtk.Label("Selected Lamp:")
        separator = gtk.HSeparator()
        vbox1.pack_start(hbox1)
        hbox1.pack_start(label,False,False,1)
        hbox1.pack_start(combobox,True,True,2)
        vbox1.pack_start(separator)
        vbox1.pack_start(color,True,True,2)
        hbox1.set_border_width(5)
        for name in lamps:
            combobox.append_text(name)
        combobox.connect('changed', self.set_lamp)
        combobox.set_active(0)
        window.show_all()
        self.lamp=lamps[0]
        loop = DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=loop)
        server = dbus.Interface( bus.get_object(avahi.DBUS_NAME, '/'), 'org.freedesktop.Avahi.Server')
        sbrowser = dbus.Interface(bus.get_object(avahi.DBUS_NAME,
        server.ServiceBrowserNew(avahi.IF_UNSPEC,
            avahi.PROTO_UNSPEC, TYPE, 'local', dbus.UInt32(0))),
        avahi.DBUS_INTERFACE_SERVICE_BROWSER)
        sbrowser.connect_to_signal("ItemNew", self.mlfound)

    def mlfound(self, interface, protocol, name, stype, domain, flags):
        print "Found service '%s' type '%s' domain '%s' " % (name, stype, domain)

        if flags & avahi.LOOKUP_RESULT_LOCAL:
                # local service, skip
                pass

        server.ResolveService(interface, protocol, name, stype,
            domain, avahi.PROTO_UNSPEC, dbus.UInt32(0),
            reply_handler=self.service_resolved, error_handler=self.print_error)

    def service_resolved(self, *args):
        print 'service resolved'
        print 'name:', args[2]
        print 'address:', args[7]
        print 'port:', args[8]

    def print_error(self, *args):
        print 'error_handler'
        print args[0]


    def set_lamp(self, combobox):
        model = combobox.get_model()
        index = combobox.get_active()
        if index:
            self.lamp = model[index][0]
            print "Active lamp: %s" % self.lamp

    def new_color(self, color):
        lamp = self.lamp
        s = uberbus.moodlamp.Moodlamp(lamp, True)
        c = color.get_current_color()
        r = c.red/256;
        g = c.green/256;
        b = c.blue/256;
        s.connect()
        s.timedfade(r,g,b,t)
        print "Setting %s to %s%s%s" % (lamp, hex(r)[2:], hex(g)[2:], hex(b)[2:])
        s.disconnect()
        return

def main():
    gtk.main()
    return

if __name__== "__main__":
    bcb = UBColorGui()
    main()