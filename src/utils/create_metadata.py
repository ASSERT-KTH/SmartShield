#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import docker


def run_mythril(bytecode, metadata, ignore_bugs=[], debug=False):
    client = docker.from_env()
    print("Running Mythril...")
    cmd = '-v 5 analyze -m ArbitraryStorage,ArbitraryDelegateCall,TxOrigin,EtherThief,IntegerArithmetics,StateChangeAfterCall,AccidentallyKillable,UncheckedRetval --bin-runtime -c '+bytecode+' --parallel-solving -o json --execution-timeout 1800'
    if debug:
        print(cmd)
    container = client.containers.run('christoftorres/mythril', cmd, detach=True, remove=False)
    for line in container.logs(stream=True):
        if debug:
            print(line)
    output = container.logs()
    output = output.decode("utf-8")
    raw = output
    output = output.split('\n')
    code_coverage = 0.0
    for line in output:
        if debug:
            print(line)
        if line.startswith("mythril.laser.plugin.plugins.coverage.coverage_plugin [INFO]: Achieved"):
            code_coverage = float(line.replace("mythril.laser.plugin.plugins.coverage.coverage_plugin [INFO]: Achieved ", "").split("%")[0])
        if line.startswith('{"'):
            result = json.loads(line)
            if result["error"] == None and result["success"] == True:
                for issue in result["issues"]:
                    if not issue["swc-id"] in ignore_bugs:
                        try:
                            if issue["swc-id"] == "107":
                                reentrancy = dict()
                                reentrancy["callOffset"] = issue["address"][0]
                                reentrancy["sStoreOffset"] = issue["address"][1]
                                metadata["Reentrancy"].append(reentrancy)
                            elif issue["swc-id"] == "101":
                                integer_bug = dict()
                                integer_bug["offset"] = issue["address"]
                                integer_bug["category"] = issue["title"].replace("Integer Arithmetic Bugs (", "").replace(")", "")[:3]
                                metadata["IntegerBugs"].append(integer_bug)
                            elif issue["swc-id"] == "104":
                                unhandled_exception = dict()
                                unhandled_exception["offset"] = issue["address"]
                                metadata["UnhandledExceptions"].append(unhandled_exception)
                        except:
                            pass
            else:
                print("Error:", result["error"])
    container.remove(force=True)
    return metadata, code_coverage, raw

def create_metadata(bytecode, ignore_bugs=[], use_assistance=False):
    metadata = {
      "Reentrancy": list(),
      "IntegerBugs": list(),
      "UnhandledExceptions": list()
    }
    code_coverage = 0.0
    metadata, code_coverage, output = run_mythril(bytecode, metadata, ignore_bugs=ignore_bugs)
    return metadata, code_coverage, output

