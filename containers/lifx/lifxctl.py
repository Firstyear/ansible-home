#!/usr/bin/python3

import lifxlan
import time
import random

import datetime

POLE = lifxlan.Light('d0:73:d5:14:18:4d', '172.24.18.12')
LOUNGE = lifxlan.Light('d0:73:d5:14:17:31', '172.24.18.10')
BEDROOM = lifxlan.Light('d0:73:d5:14:0d:b9', '172.24.18.13')

# Lifix lan has colours, but we take some ideas here.

def show_all_name_and_details():
    lan = lifxlan.LifxLAN()
    lights = lan.get_lights()
    print(lights)
    for l in lights:
        label = l.get_label()
        mac = l.get_mac_addr()
        addr = l.get_ip_addr()
        print("%s -> '%s' '%s'" % (label, mac, addr))
        print(l.get_color())

def _determine_redshift_colour(current_time):
    DAY_START = 7
    DAY_END = 16
    EVENING_END = 17
    NIGHT_END = 19
    # from 8 am to say .... 4 pm? just set the value
    if current_time.hour >= DAY_START and current_time.hour < DAY_END:
        return (0, 0, 65535, 4000)
    # from 4pm to 7 pm start to dim down to 45000
    elif current_time.hour >= DAY_END and current_time.hour < EVENING_END:
        # Get the number of minutes between now and the end
        hours_rem = EVENING_END - current_time.hour
        min_tot = (EVENING_END - DAY_END) * 60
        min_rem = ((hours_rem * 60) - current_time.minute)

        brightness = 45000 + (20535 * (min_rem / min_tot))
        return (0, 0, int(brightness), 4000)
    # from 7pm to 9 pm dim + reduce temp
    elif current_time.hour >= EVENING_END and current_time.hour < NIGHT_END:
        hours_rem = NIGHT_END - current_time.hour
        min_tot = (NIGHT_END - EVENING_END) * 60
        min_rem = ((hours_rem * 60) - current_time.minute)

        brightness = 33000 + (12000 * (min_rem / min_tot))
        colour = 2750 + (1250 * (min_rem / min_tot))
        return (0, 0, int(brightness), int(colour))
    else:
        # Must be overnight (or early morning)
        return (0, 0, 33000, 2750)

def redshift(current_time):
    # Based on time of day set appropriate brightness and temperature.
    # Evening go to (0, 0, 33000, 2750)
    # Daytime go to (0, 0, 65535, 4000)
    #
    # Bedroom takes different settings, so don't touch that.
    colour = _determine_redshift_colour(current_time)
    print (colour)

    # Don't mind exceptions, we are probably offline.
    try:
        LOUNGE.set_color(colour, 5000, True)
    except:
        pass
    try:
        POLE.set_color(colour, 5000, True)
    except:
        pass

def party_hard():
    # Cycle between some cool colours.
    # After a certain time stop and kill our marker file.
    colours = [lifxlan.BLUE, lifxlan.RED, lifxlan.GREEN, lifxlan.ORANGE, lifxlan.GOLD, lifxlan.YELLOW]

    while True:
        c = random.choice(colours)
        POLE.set_color(c, 2000, True)
        POLE.set_color(c, 2000, True)
        c = random.choice(colours)
        LOUNGE.set_color(c, 2000, True)
        LOUNGE.set_color(c, 2000, True)
        time.sleep(2)

if __name__ == '__main__':
    print("Starting LIFX control ...")
    # show_all_name_and_details()
    party_hard_on = False

    while True:

        current_time = datetime.datetime.now().time()
        # for i in range(16, 22):
        #     for m in (0, 15, 30, 45):
        #         current_time = datetime.time(i,m)
        #         print(current_time)
        #         redshift(current_time)

        if party_hard_on:
            party_hard()
        else:
            redshift(current_time)
        time.sleep(60)


