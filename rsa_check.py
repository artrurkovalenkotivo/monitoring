#!/usr/bin/env python3

"""Hello world Nagios check."""

import nagiosplugin
import time

from shared_lib import system


class ADBRSA(nagiosplugin.Resource):

    def probe(self):
        system.cmd("adb connect 10.101.119.11")
        time.sleep(0.5)
        output = system.cmd("adb devices | grep 10.101.119.11")
        state = "device" in output
        system.cmd("adb disconnect 10.101.119.11")
        return [nagiosplugin.Metric('rsa', state, context='null')]


def main():
    check = nagiosplugin.Check(ADBRSA())
    check.main()


if __name__ == '__main__':
    main()
