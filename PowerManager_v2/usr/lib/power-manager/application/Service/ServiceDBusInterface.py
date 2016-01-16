# Copyright 2015 Alex Woroschilow (alex.woroschilow@gmail.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import dbus.service
import json, sys, dbus, inspect
from vendor.EventDispatcher import Event
from dbus import DBusException
from gi.repository import GObject
from dbus.mainloop.glib import DBusGMainLoop

from vendor.DBusListeners import *
import vendor.DBusListeners as Clients


class ServiceDBusInterface(dbus.service.Object):
    def __init__(self, container):
        self.container = container
        pass

    @property
    def listeners(self):
        return self.__listeners
        pass

    @property
    def is_battery(self):
        for listener in self.listeners:
            is_use_battery = listener.is_battery
            if is_use_battery is not None:
                if not is_use_battery:
                    return False
        return True
        pass

    @dbus.service.method('org.sensey.PowerManager')
    def optimize(self, options=None):
        service_logger = self.container.get("logger")
        service_logger.debug("[ServiceDBusInterface] optimize")
        service_event_dispatcher = self.container.get("event_dispatcher")
        service_event_dispatcher.dispatch('app.on_powersafe' if self.is_battery else 'app.on_perfomance', Event())
        pass

    @dbus.service.method('org.sensey.PowerManager')
    def powersave(self, options):
        service_logger = self.container.get("logger")
        service_logger.debug("[ServiceDBusInterface] powersave")
        service_event_dispatcher = self.container.get("event_dispatcher")
        service_event_dispatcher.dispatch('app.on_powersafe', Event())
        pass

    @dbus.service.method('org.sensey.PowerManager')
    def perfomance(self, options):
        service_logger = self.container.get("logger")
        service_logger.debug("[ServiceDBusInterface] perfomance")
        service_event_dispatcher = self.container.get("event_dispatcher")
        service_event_dispatcher.dispatch('app.on_perfomance', Event())
        pass

    @dbus.service.method('org.sensey.PowerManager')
    def status(self, options):
        response = {}
        for switcher in self.container.get("power_manager").switchers:
            response[switcher.__str__()] = switcher.is_powersave
        return json.dumps(response)
        pass

    @dbus.service.signal(dbus_interface='org.sensey.PowerManager', signature='')
    def status_changed(self):
        service_logger = self.container.get("logger")
        service_logger.debug("[ServiceDBusInterface] status_changed")
        pass

    def on_loaded(self, event, dispatcher):
        service_event_dispatcher = self.container.get("event_dispatcher")
        service_event_dispatcher.addListener('app.on_status_changed', self.on_status_changed)
        pass

    def on_started(self, event, dispatcher):
        DBusGMainLoop(set_as_default=True)
        try:

            bus = dbus.SystemBus()
            self.__listeners = []
            for (name, module) in inspect.getmembers(Clients, inspect.ismodule):
                if hasattr(module, name):
                    identifier = getattr(module, name)
                    self.__listeners.append(identifier(bus, self, None))

            dbus.service.Object.__init__(self, dbus.service.BusName("org.sensey.PowerManager", bus),
                                         "/org/sensey/PowerManager")

            self.optimize(None)

        except DBusException as exception:
            print(exception.get_dbus_message())
            sys.exit(0)
        (GObject.MainLoop()).run()

        pass

    def on_status_changed(self, event, dispatcher):
        self.status_changed()
        pass
