FROM python:3.13

#Set number of plugins to analyse
ENV NUM_PLUGINS=10 DB_NAME="semgrep_analysis.db"

#semgrep & joern installation
RUN apt-get update && apt-get upgrade -y
RUN python3 -m pip install semgrep duckdb
RUN apt-get install -y openjdk-21-jdk
ADD "https://github.com/joernio/joern/releases/latest/download/joern-install.sh" /
RUN chmod +x ./joern-install.sh \
    ./joern-install.sh
#verify installation
RUN semgrep --version
RUN java --version


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

