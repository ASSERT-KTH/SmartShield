import json
import subprocess
import sys
import os

def use_solc(version):
    install = f"solc-select install {version}"
    use = f"solc-select use {version}"
    try:
        process = subprocess.run(install, shell=True, check=True)
        process = subprocess.run(use, shell=True, check=True)

        return process.returncode == 0
    except:
        return False

def run_smartshields(path, main, outdir):
    cmd = f"python run_smartshields.py -s {path} -m {main} -o {outdir} -t {60*60*2}"
    try:
        process = subprocess.run(cmd, shell=True, capture_output=True, timeout=60*60*2)
    except subprocess.TimeoutExpired:
        return -1
    return process.returncode

def process_entry(path, contract, results, version):
    elements = path.split("/")
    outdir = os.path.join(results, elements[-2])
    prev = os.path.join(outdir, elements[-1].replace(".sol", ""), elements[-1].replace(".sol", ".out"))
    # print(prev)
    if os.path.exists(prev):
        print("Skipping", path)
        return 0
    ret = use_solc(version)
    print(f"{path}: {ret}")
    if not ret:
        return -1
    os.makedirs(outdir, exist_ok=True)
    return run_smartshields(path, contract, outdir)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python run_smartbugs.py <smartbugs> <results>")
        sys.exit(1)

    smartbugs = sys.argv[1]
    results = sys.argv[2]

    vuln_json = os.path.join(smartbugs, "vulnerabilities.json")
    with open(vuln_json, 'r') as file:
        data = json.load(file)
    
    for entry in data:
        # if entry.get('path') == "dataset/access_control/FibonacciBalance.sol" or entry.get('path') == "dataset/access_control/parity_wallet_bug_2.sol":
        #     continue
        print(entry.get('path'))
        path = os.path.join(smartbugs, entry.get('path'))
        contract = entry.get('contract_names')[0]
        version = "0.4.24"
        if entry.get('path') == "dataset/access_control/parity_wallet_bug_1.sol":
            version = "0.4.9"
        if path and contract:
            ret = process_entry(path, contract, results, version)
            # write results in csv file
            with open(os.path.join(results, "results.csv"), 'a') as f:
                f.write(f"{path},{contract},{ret}\n")
        else:
            print("Invalid entry in JSON:", entry)