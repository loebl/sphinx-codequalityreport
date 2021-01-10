#!/usr/bin/python3

import copy
import hashlib
import json
import os
import re
import sys

issues = []

# Variable parts of an issue
# - check name: based on the warning string, there should be only a finite amount of warnings
#   in sphinx. V1: maybe always the same check name for simplicity
# - description: V1: verbatim warning text
# - categories: ???, V1: always "Style"
# - location: get line number and file from warning string
# all warnings come on stderr -> can probably be redirected into separate file
# BUT I still want to see them in the Gitlab job log
# Add options: "-w warn.log -N" (write warnings to file, disable color output)

default_issue = {}
default_issue["type"] = "issue" # req: type is always issue
default_issue["check_name"] = "Sphinx/Parsing" # req: which check emitted issue
# req: short description of issue
default_issue["description"] = ""
# optional: content. Longer description of issue, in markdown
# req: categories of problems
# categories given by the spec:
# - Bug Risk
# - Clarity
# - Compatibility
# - Complexity
# - Duplication
# - Performance
# - Security
# - Style
# Only style would probably be matching for sphinx. So I would try custom categories first, how
# they are received by Gitlab. But which categories should I use?
default_issue["categories"] = ["Style"]
# req: location description
# locations contain a path to a file and either lines or positions
# lines are 1-based, and begin and end are both inclusive
default_issue["location"] = { "path": "",
        "lines": {
            "begin": 1,
            "end": 1
            }
        }
# optional: trace. other locations relevant for this issue
# optional: remediation points: integerindicating roughly the effort required to solve this
# issue
# optional: severity string (Gitlab: required)
default_issue["severity"] = "minor"
# optional: fingerprint to uniquely identify the issue (Gitlab: required)


# print(json.dumps(default_issue, indent=2))

if len(sys.argv) < 2:
    print("Require warning file name (generate with \"-w warn.log\") as input")
    exit(1)

# Checki f sys.argv[1] is a file that exists
warnlog = sys.argv[1]
if not os.path.exists(warnlog):
    print("Given warnlog does not exist")
    exit(1)
line_matcher = re.compile(r"(.*\.rst):?(\w*):?\s?WARNING: (.*)")
with open(warnlog) as warn_file:
    # Read in line by line
    for line in warn_file:
        parts = list(map(str.rstrip, map(str.lstrip, line.split(":"))))
        # On each line, parse warnings:
          # <filepath>:<linunum>: WARNING: <description>
          # <filepath>: WARNING: <description>
          # WARNING: <description>
          # the second case only appears for global/not file specific warnings (for example missing
          # static path for HTML)
          # (there might be more/different for errors)
        if parts[0] == "WARNING":
            # general warning, skip those
            continue
        new_issue = copy.deepcopy(default_issue)
        new_issue["location"]["path"] = parts[0]
        new_issue["description"] = parts[-1]
        if not parts[1] == "WARNING":
            new_issue["location"]["lines"]["begin"] = parts[1]
            new_issue["location"]["lines"]["end"] = parts[1]
            new_issue["fingerprint"] = hashlib.md5(parts[0].join(parts[1]).encode()).hexdigest()
        else:
            new_issue["fingerprint"] = hashlib.md5(parts[0].encode()).hexdigest()
        issues.append(new_issue)

print(json.dumps(issues, indent=2))
