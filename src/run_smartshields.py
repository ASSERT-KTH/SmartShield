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
                        type=str, required=True, help='Solidity file or bytecode file (default: solidity)')
    parser.add_argument('-b', '--bytecode',
                        type=bool, default=False, help='If source is bytecode file, set this flag')
    parser.add_argument('-m', '--main',
                        type=str, required=True, help='Main contract name in the solidity file')
    parser.add_argument('-t', '--timeout',
                        type=int, default=60,
                        help='Timeout for analyzing and patching in seconds (default to 60 seconds)')
    parser.add_argument('-o', '--output',
                        type=str, required=True, help='Output directory')
    parser.add_argument('-r', '--report',
                        type=str, help='Patching report file (JSON)')
    parser.add_argument('-d', '--debug',
                        action='store_true', help='Debug output')
    args = parser.parse_args()


    bytecode = None
    file = args.source
    filename = os.path.basename(file)
    filename = os.path.join(os.path.abspath(args.output), filename)
    compiled_file = filename.replace(".sol", ".rt.hex")

    if not args.bytecode:
        print("Compiling solidity file...")
        main = args.main
        bytecode = compile_solidity_file(file, main, compiled_file)
    else:
        with open(args.source, "r") as f:
            bytecode = f.read()

    print("Creating metadata...")
    metadata, code_coverage, output = create_metadata(bytecode)
    
    metadata_file = filename.replace(".sol", ".metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)

    output_file = filename.replace(".sol", ".mythril.log")
    with open(output_file, "w") as f:
        f.write(output)

    patched_file = filename.replace(".sol", ".patched.sol")
    
    print("Running Smartshield...")
    process = subprocess.run(f"python evm_rewriter.py -b {compiled_file} -m {metadata_file} -t {args.timeout} -o {patched_file} -r {args.report} {'-d' if args.debug else ''}", shell=True, capture_output=True)

    print(process.stdout.decode())

    print(process.stderr.decode())
    

if __name__ == "__main__":
    main()
