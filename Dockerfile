### Alternative for cuda enabled environment: cnstark/pytorch:2.0.1-py3.10.11-cuda11.8.0-ubuntu22.04
FROM cnstark/pytorch:2.0.1-py3.10.11-ubuntu22.04
#LABEL ppp
#AUTHOR ccc

ENV USERID 1000
ENV DEBIAN_FRONTEND noninteractive

RUN useradd -m -u ${USERID} user
WORKDIR /home/user

RUN apt-get update
RUN apt-get install -y git-lfs zip unzip wget
RUN GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/Salesforce/codet5-base
RUN rm codet5-base/pytorch_model.bin

RUN wget https://zenodo.org/records/7229913/files/BinT5.zip?download=1 -O bint5.zip
RUN unzip bint5.zip
RUN rm bint5.zip

RUN pip install transformers matplotlib pandas seaborn nltk numpy tqdm rouge
RUN python -c "import nltk; nltk.download('wordnet')"
COPY main.py .
COPY LICENSE .
COPY ELAB.py .

RUN chown ${USERID} -R .
USER ${USERID}
RUN python -c "import nltk; nltk.download('wordnet')"

