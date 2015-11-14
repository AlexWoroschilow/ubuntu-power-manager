import os
import os.path


class Watchdog():

    def __init__(self):
        pass


    """
    Check is all devices, handled by this object
    are in powersave mode, if on of those is not,
    that means that all module is not in powersave mode
    """
    @property
    def is_powersave(self):
        for power_control in self.devices:
            if os.path.isfile(power_control):
                if '0' not in self._run("cat %s" % power_control):
                    return False
        return True


    """
    Get list of devices to handle with
    """
    @property
    def devices(self):
        return ["/proc/sys/kernel/nmi_watchdog"]


    """
    Switch to powersave mode all devices,
    handled by this object, this method already 
    should return just a list with shell commands
    """
    def powersave(self):
        commands = []
        for power_control in self.devices:
            if os.path.isfile(power_control):
                commands.append("echo '0' > '%s';" % power_control)
        return commands


    """
    Enable perfomance mode of devices, 
    handled by this object, this method already should 
    return just a list of shell commands
    """
    def perfomance(self):
        commands = []
        for power_control in self.devices:
            if os.path.isfile(power_control):
                commands.append("echo '1' > '%s';" % power_control)
        return commands


    """
    Run command locally, needs to get statuses of devices 
    and so on, do not use this function to switch device state
    """
    def _run(self, command):
        return os.popen(command).read()


    """
    Get name of current switcher, 
    users can see this names, needs to work with 
    translations for this strings
    """
    def __str__(self):
        return "Watchdog optimisations"
    
    
if __name__ == "__main__":
    print((Watchdog()).devices, (Watchdog()).is_powersave)
    print((Watchdog()).powersave())
    print((Watchdog()).perfomance())