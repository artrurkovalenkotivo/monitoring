#!/usr/bin/env python3

"""Hello world Nagios check."""
import argparse
import logging
import random
import re
import shlex
import subprocess

import nagiosplugin

MW_LIST = "mwcap-info -l"
MW_INFO = "mwcap-info --info-all"
TEST_l4 = """total: 4
device path     firmware ver    hardware ver    driver ver      alsa name       device name
/dev/video0     1.34            B               1.3.4236        hw:0,0          01:01 Pro Capture Dual HDMI 4K+
/dev/video1     1.34            B               1.3.4236        hw:1,0          01:00 Pro Capture Dual HDMI 4K+
/dev/video2     1.34            B               1.3.4236        hw:2,0          00:01 Pro Capture Dual HDMI 4K+
/dev/video3     1.34            B               1.3.4236        hw:3,0          00:00 Pro Capture Dual HDMI 4K+
"""
TEST_l0 = """total: 0
"""

TEST_info = """Device
  Family name ............................ Pro Capture
  Product name ........................... Pro Capture Dual HDMI 4K+
  Firmware name .......................... High Performance Firmware
  Serial number .......................... B126210609070
  Hardware version ....................... B
  Firmware version ....................... 1.34
  Driver version ......................... 1.3.4236
  Board ID ............................... 0
  Channel ID ............................. 0
  Bus address ............................ bus 14, device 0
  PCIe speed ............................. gen 2
  PCIe width ............................. x4
  Max playload size ...................... 256 Bytes
  Max read request szie .................. 128 Byt
  Signal status .......................... {status}"""


class Signal(nagiosplugin.Resource):

    def __init__(self, *args, **kwargs):
        self._log = logging.getLogger("nagiosplugin")
        self._debug = kwargs.get("debug")
        self._target_port = kwargs.get("port")
        self._exclude = kwargs.get("exclude", [])
        self.installed_cards = []
        self.valid_cards = []

    def __stub(self, cmd):
        if MW_LIST in cmd:
            output = random.choice((TEST_l0, TEST_l4))
        elif MW_INFO in cmd:
            output = TEST_info.format(status=random.choice(("None", "Valid", "Invalid", "Locked")))
        else:
            output = f"No stub for: '{cmd}'"
        return output

    def _exec(self, cmd, error_ok=True):
        cmd_posix = shlex.split(cmd)
        try:
            output = subprocess.check_output(cmd_posix, timeout=30).decode("utf-8", "replace")
        except (subprocess.SubprocessError, FileNotFoundError) as err:
            output = "error"
            if self._debug:
                output = self.__stub(cmd)
            self._log.debug(f"CMD: '{cmd}', failed: '{err}'")
            if not error_ok:
                raise nagiosplugin.CheckError(f'cannot run {cmd}')
        return output

    def get_cards_ids(self):
        self._log.info("Querying available cards")
        if self.installed_cards:
            ids = self.installed_cards
        else:
            cmd = "mwcap-info -l"
            output = self._exec(cmd)
            parser = re.compile(r"\d{2}:\d{2}")
            ids = []
            for line in output.split("\n"):
                result = parser.search(line)
                if result:
                    ids.append(result.group())
            self.installed_cards = ids
        self._log.info(f"Detected {len(ids)} cards")
        if self._target_port and self._target_port in ids:
            ids = [self._target_port]
        elif self._target_port and self._target_port not in ids:
            raise nagiosplugin.CheckError(f'Port {self._target_port} is not detected. Available: {ids}')
        return ids

    def get_card_info(self, port):
        cmd = f"mwcap-info --info-all {port}"
        output = self._exec(cmd)
        self._log.debug(f"Info: {output}")
        info = dict()
        for line in output.split("\n"):
            try:
                parser = re.search(r"(\w+.*\w+)( [\.]{3,} )(\w+.*\w+|\d)", line)
                if "Serial" in line and parser:
                    info['sn'] = parser.group(3)
                elif "Signal status" in line and parser:
                    info['signal'] = parser.group(3)
            except Exception as e:
                raise LookupError(f"Failed to get device info.\nError: {e}.\nOutput - {output}.")
        self._log.info(f"Port {port} raw status: {info.get('signal')}")
        self._log.debug(f"Port {port}: {info}")
        return info

    def probe(self):
        self.installed_cards = self.get_cards_ids()
        if self.installed_cards:
            for port in self.installed_cards:
                if port in self._exclude:
                    continue
                info = self.get_card_info(port)
                if info.get("signal") in ("Valid", "Locked"):
                    status = 1
                    self.valid_cards.append(port)
                else:
                    status = -1
                yield nagiosplugin.Metric(f'{port}',
                                          status,
                                          context="signal"
                                          )
        else:
            yield nagiosplugin.Metric('NA',
                                      0,
                                      context="signal"
                                      )


class SignalSummary(nagiosplugin.Summary):

    def ok(self, results):
        return f"{len(results)} ports are valid"

    def problem(self, results):
        list_to_show = []
        for res in results:
            if res.state.code == 2:
                # find critical only
                list_to_show.append(res.metric.name)
        if len(list_to_show) == 0:
            msg = "No available ports"
        else:
            msg = f"Signal is invalid on: {len(list_to_show)} port(s)"
        return msg


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('-p', '--port',
                      help='specific port to check signal')
    argp.add_argument('-d', '--sandbox', action="store_true",
                      help='specific port to check signal')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')
    argp.add_argument('-e', '--exclude', action='append',
                      help='Exclude listed ports for analysis')
    args = argp.parse_args()
    mw_check = Signal(debug=args.sandbox, port=args.port, exclude=args.exclude)
    check = nagiosplugin.Check(
        mw_check,
        nagiosplugin.ScalarContext("signal",
                                   warning="1:1",
                                   critical=f"0:1",
                                   fmt_metric="For port {name} signal status is: {value}"),
        SignalSummary(),
    )
    check.main(verbose=args.verbose,
               timeout=200)


if __name__ == '__main__':
    main()
