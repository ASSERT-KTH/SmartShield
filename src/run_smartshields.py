import argparse
import json
import os
import subprocess
from utils.compile_solidity import compile_solidity_file
from utils.create_metadata import create_metadata


def main():
    print("Running Smartshield wrapper...")

    parser = argparse.ArgumentParser(description='Wrapper for Smartshield')
    parser.add_argument('-s', '--source',
                        type=str, required=False, help='Solidity file or bytecode file (default: solidity)')
    parser.add_argument('-b', '--bytecode',
                        type=bool, default=False, help='If source is bytecode file, set this flag')
    parser.add_argument('-m', '--main',
                        type=str, required=True, help='Main contract name in the solidity file')
    parser.add_argument('-t', '--timeout',
                        type=int, default=60,
                        help='Timeout for analyzing and patching in seconds (default to 60 seconds)')
    parser.add_argument('-o', '--output',
                        type=str, required=True, help='Output directory')
    parser.add_argument('-d', '--debug',
                        action='store_true', help='Debug output')
    args = parser.parse_args()


    bytecode = None
    file = args.source
    filename = os.path.basename(file)
    output_dir = os.path.join(os.path.abspath(args.output), filename.split(".")[0])
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, filename)
    compiled_file = filename.replace(".sol", ".rt.hex")
    print( args.bytecode)

    if not args.bytecode:
        print("Compiling solidity file...")
        main = args.main
        bytecode = compile_solidity_file(file, main, compiled_file)
        print("Bytecode compiled")
        print(bytecode)
    else:
        with open(args.source, "r") as f:
            bytecode = f.read()

    print("Creating metadata...")
    metadata, code_coverage, output = create_metadata(bytecode)
    print("Metadata: ", metadata)
    metadata_file = filename.replace(".sol", ".metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    mythril_file = filename.replace(".sol", ".mythril.log")
    with open(mythril_file, "w") as f:
        f.write(output)

    patched_file = filename.replace(".sol", ".bin")
    report_file = filename.replace(".sol", ".report.json")
    
    print("Running Smartshield...")
    process = subprocess.run(f"python evm_rewriter.py -b {compiled_file} -m {metadata_file} -t {args.timeout} -o {patched_file} -r {report_file} {'-d' if args.debug else ''}", shell=True, capture_output=True)
    print("Smartshield finished")
    output_file = filename.replace(".sol", ".out")
    with open(output_file, "w") as f:
        f.write(process.stdout.decode())

    log_file = filename.replace(".sol", ".log")
    with open(log_file, "w") as f:
        f.write(process.stderr.decode())
    
    exit(process.returncode)    

if __name__ == "__main__":
    main()
