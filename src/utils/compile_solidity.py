import subprocess


def compile_solidity_file(path, main, output_file):
    try:
        cmd = f"./utils/compile_solidity.sh {path} {main} {output_file}"
        process =subprocess.run(cmd, shell=True, capture_output=True)
        print(process.stderr.decode())
        with open(output_file, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error compiling solidity file: {e}")
        return None
