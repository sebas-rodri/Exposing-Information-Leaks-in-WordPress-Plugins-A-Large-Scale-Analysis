FROM python:3.13.5-slim-bookworm

#Set number of plugins to analyse
ENV NUM_PLUGINS=10

RUN apt-get update && apt-get upgrade -y
RUN python3 -m pip install semgrep
#verify installation
RUN semgrep --version


WORKDIR /static_analysis

#Required Files for static analysis
COPY download-and-unzip.py .
COPY requirements.txt .
COPY plugins_sorted.csv .
COPY semgrep-rules.yml .

#Make entrypoint executable
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

