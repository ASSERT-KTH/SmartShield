FROM python:3.8

WORKDIR /smartshield
COPY . /smartshield

# Install SMARTSHIELD
RUN python -m pip install -r requirements.txt

ENTRYPOINT ["python", "/smartshield/src/evm_rewriter.py"]
