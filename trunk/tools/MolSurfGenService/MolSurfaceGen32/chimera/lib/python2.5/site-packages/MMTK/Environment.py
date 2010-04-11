# This module defines environment objects for universes.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

from Scientific import N as Numeric

#
# The environment object base class
#
class EnvironmentObject:

    is_environment_object = 1

    def checkCompatibilityWith(self, other):
        pass

    def description(self):
        return "o('Environment." + self.__class__.__name__ + \
               `self.arguments` + "')"

# Type check

def isEnvironmentObject(object):
    return hasattr(object, 'is_environment_object')

#
# Nose thermostat class
#
class NoseThermostat(EnvironmentObject):

    """Nose thermostat for Molecular Dynamics

    A thermostat object can be added to a universe and will then
    modify the integration algorithm to a simulation of an NVT
    ensemble.

    Constructor:  NoseThermostat(|temperature|, |relaxation_time|=0.2)

    Arguments:

    |temperature| -- the temperature set by the thermostat

    |relaxation_time| -- the relaxation time of the thermostat coordinate
    """

    def __init__(self, temperature, relaxation_time = 0.2):
        self.arguments = (temperature, relaxation_time)
        self.parameters = Numeric.array([temperature, relaxation_time])
        self.coordinates = Numeric.array([0., 0.])

    def setTemperature(self, temperature):
        self.parameters[0] = temperature

    def setRelaxationTime(self, t):
        self.parameters[1] = t

    def checkCompatibilityWith(self, other):
        if other.__class__ is NoseThermostat:
            raise ValueError("the universe already has a thermostat")

#
# Andersen barostat class
#
class AndersenBarostat(EnvironmentObject):

    """Andersen barostat for Molecular Dynamics

    A barostat object can be added to a universe and will then
    together with a thermostat object modify the integration algorithm
    to a simulation of an NPT ensemble.

    Constructor:  AndersenBarostat(|pressure|, |relaxation_time|=1.5)

    Arguments:

    |pressure| -- the pressure set by the barostat

    |relaxation_time| -- the relaxation time of the barostat coordinate
    """

    def __init__(self, pressure, relaxation_time = 1.5):
        self.arguments = (pressure, relaxation_time)
        self.parameters = Numeric.array([pressure, relaxation_time])
        self.coordinates = Numeric.array([0.])

    def setPressure(self, pressure):
        self.parameters[0] = pressure

    def setRelaxationTime(self, t):
        self.parameters[1] = t

    def checkCompatibilityWith(self, other):
        if other.__class__ is AndersenBarostat:
            raise ValueError("the universe already has a barostat")

