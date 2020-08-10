#!/usr/bin/env python3

import subprocess
import requests
import re
import os

VERBOSE = True
ONLY_ACTIVE = True  # Delete some inaccesible domains
OUTPUT_DIRECTORY = "output"  # Directory to save found domains


def get_tlds():
    print("[  LOG  ] Downloading TLD list")
    tld = requests.get(
        "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
    ).text.splitlines()
    torm = []
    for i in range(len(tld)):
        if re.search(r"XN\-\-.*", tld[i]) is not None:
            torm.append(i)
    del tld[torm[0] : torm[-1] + 1], tld[0]
    tld.append("xn")
    tld = [e.lower() for e in tld]
    print(f"[  LOG  ] Downloaded {len(tld)} TLDs")
    return tld


def get_domains(tld):
    out = subprocess.getoutput(f"subfinder -silent -d {tld}").splitlines()
    print(f"[  LOG  ] Found {len(out)} domains for .{tld} TLD")
    if ONLY_ACTIVE:
        before = len(out)
        for e in out:
            outc = os.system(f"ping -c 1 -w 3 {e} >/dev/null 2>&1")
            if outc != 0:
                if VERBOSE:
                    print(f"[  LOG  ] Domain {e} is inaccesible, removing")
                out.remove(e)
        after = len(out)
        if before != after:
            print(f"[  LOG  ] Deleted {before - after} inaccesible domains")
    return out


def main():
    tlds = get_tlds()
    domains = {}
    for tld in tlds:
        print(f"[  LOG  ] Scanning .{tld} TLD")
        domains[tld] = get_domains(tld)
        with open(f"{OUTPUT_DIRECTORY}/{tld}", "w") as f:
            f.write("\n".join(domains[tld]))


if __name__ == "__main__":
    main()
