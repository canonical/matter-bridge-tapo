#
#    Copyright (c) 2021 Project CHIP Authors
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

from threading import Thread, Event
from chip.server import (
    GetLibraryHandle,
    NativeLibraryHandleMethodArguments,
    PostAttributeChangeCallback,
)

from chip.exceptions import ChipStackError

import json
import time
import subprocess
import os


from PyP100 import PyL530, PyP100, PyP110

partyOn = None
partyThread = None
endpoints = []
defaults = None
envAudioFilePath = os.getenv('AUDIO_FILE')
envConfFilePath = os.getenv('CONF_FILE')


def switch_on(dev: dict):

    type = dev['type']

    # Initialize level and color on first request
    if type == 'bulb' and 'set' not in defaults:
        set_level(dev, defaults['brightness'])
        set_color(dev, defaults['hue'], defaults['sat'])
        defaults['set'] = True

    ip = dev['ip']
    driver = dev['driver']

    print("[tapo] {}@{}: switch on".format(type, ip))
    driver.turnOn()


def switch_off(dev: dict):

    type = dev['type']
    ip = dev['ip']
    driver = dev['driver']

    print("[tapo] {}@{}: switch off".format(type, ip))
    driver.turnOff()


def set_level(dev: dict, level: int):

    type = dev['type']
    ip = dev['ip']
    driver = dev['driver']

    print("[tapo] {}@{}: set brightness level: {}".format(type, ip, level))
    driver.setBrightness(level)


def set_color(dev: dict, hue: int, saturation: int):

    type = dev['type']
    ip = dev['ip']
    driver = dev['driver']

    print("[tapo] {}@{}: set color: {}, {}".format(type, ip, hue, saturation))
    driver.setColor(hue, saturation)


def party():
    global partyOn
    # find the devices
    plugs, bulbs = [], []
    party = None
    for device in endpoints.values():
        match device['type']:
            case 'plug':
                plugs.append(device)
            case 'bulb':
                bulbs.append(device)
            case 'party':
                party = device

    for d in plugs + bulbs:
        switch_on(d)

    for b in bulbs:
        set_level(b, defaults['brightness'])

    # play the music
    audioFile = party['audioFile']  # from config file
    if envAudioFilePath:
        audioFile = envAudioFilePath  # from env var
    musicProc = subprocess.Popen(['mpg123', audioFile])
    delay = party['transitionDelay']

    while partyOn:
        for color in party['colors']:
            for b in bulbs:
                set_color(b, color['hue'], color['sat'])
            time.sleep(delay)

            if not partyOn:  # interrupt the party
                break

    print("Party is over.")
    # set the default light color
    for b in bulbs:
        set_color(b, defaults['hue'], defaults['sat'])
    # switch everything off
    for d in plugs + bulbs:
        switch_off(d)
    # stop the music
    musicProc.terminate()


@PostAttributeChangeCallback
def attributeChangeCallback(
    endpoint: int,
    clusterId: int,
    attributeId: int,
    xx_type: int,
    size: int,
    value: bytes,
):
    print("[callback] endpoint={} cluster={} attr={} value={}".format(
        endpoint, clusterId, attributeId, list(value)))

    if 1 <= endpoint <= 3:  # Tapo devices
        dev = endpoints[str(endpoint)]
        # switch
        if clusterId == 6 and attributeId == 0:
            if value and value[0] == 1:
                print("[callback] on")
                switch_on(dev)
            else:

                print("[callback] off")
                switch_off(dev)

        else:
            print("[callback] Error: unhandled cluster {} or attribute {}".format(
                clusterId, attributeId))
            pass

    elif endpoint == 4:  # Party mode
        if clusterId == 6 and attributeId == 0:
            global partyOn
            if value and value[0] == 1:
                global partyThread
                print("[callback] on")
                if not partyOn:
                    partyOn = True
                    partyThread = Thread(target=party)
                    partyThread.start()
            else:
                print("[callback] off")
                partyOn = False

    else:
        print("[callback] Error: unhandled endpoint {} ".format(endpoint))


class Lighting:
    def __init__(self):
        self.chipLib = GetLibraryHandle(attributeChangeCallback)


if __name__ == "__main__":
    print("Starting Tapo Bridge Lighting App")

    confFilePath = "config.json"
    if envConfFilePath:
        confFilePath = envConfFilePath
    confFile = open(confFilePath)
    conf = json.load(confFile)
    confFile.close()

    endpoints = conf['endpoints']
    defaults = conf['defaults']

    user = conf['tplinkUsername']
    password = conf['tplinkPassword']
    if not user or not password:
        print("TP-Link account username or password is unset!")
        quit(1)
    for id, device in endpoints.items():
        type = device['type']
        match type:
            case 'bulb' | 'plug':
                ip = device['ip']
                model = device['model']
                match model:
                    case 'L530':
                        endpoints[id]['driver'] = PyL530.L530(
                            ip, user, password)
                    case 'P100/P105':
                        endpoints[id]['driver'] = PyP100.P100(
                            ip, user, password)
                    case 'P110/P115':
                        endpoints[id]['driver'] = PyP110.P110(
                            ip, user, password)
                    case other:
                        print('ERROR: Unsupported device model:', model)
                        quit(1)

                driver = endpoints[id]['driver']
                print("[tapo] {}@{}: handshake".format(type, ip))
                driver.handshake()
                print("[tapo] {}@{}: login".format(type, ip))
                driver.login()
                print("[tapo] {}@{}: ready ✅".format(type, ip))
                # print(driver.getDeviceInfo())
            case 'party':
                # Nothing to initialize
                pass
            case other:
                print('ERROR: Unknown device type:', type)
                quit(1)

    l = Lighting()

    print('🚀 Ready...')
    Event().wait()
