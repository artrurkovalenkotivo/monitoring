#!/usr/bin/env python3
import argparse

import requests

import logging


def check_agent(server, agent):
    url = f"{server.strip()}/computer/{agent.strip()}/api/json"
    log = logging.getLogger("agent_checker")
    try:
        response = requests.get(url, timeout=15)
        if response.ok:
            log.info("Jenkins responded OK. Parsing...")
            agent_statistic = response.json()
            log.debug(f"Response: {agent_statistic}")
            if agent_statistic.get('offline'):
                cause = agent_statistic.get("offlineCause")
                reason = agent_statistic.get("offlineCauseReason") or "Offline"
                log.info(f"Agent status: {reason}/{cause}")
                if agent_statistic.get("temporarilyOffline"):
                    check_result = f"WARNING - {reason}, {cause}"
                else:
                    check_result = f"CRITICAL - {reason}, {cause}"
            else:
                log.info(f"Agent offline: {agent_statistic.get('offline')}")
                check_result = "OK - agent is alive"
        else:
            log.debug(f"Request failed: {response}")
            check_result = f"WARNING - {response.reason}"
    except requests.RequestException as err:
        check_result = f"WARNING - API failed {err}"
    return check_result


def main():
    argp = argparse.ArgumentParser()
    argp.add_argument('-s', '--server',
                      help='Address of Jenkins server')
    argp.add_argument('-a', '--agent',
                      help='Name of agent to check')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase output verbosity (use up to 3 times)')

    args = argp.parse_args()
    level = 50 - args.verbose * 10
    logging.basicConfig(level=level)
    print(check_agent(args.server, args.agent))


if __name__ == '__main__':
    main()
