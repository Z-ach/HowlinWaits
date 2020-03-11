FROM tensorflow/tensorflow:latest-gpu-py3
RUN mkdir -p /usr/home/app
WORKDIR /usr/home/app
ADD requirements.txt .
RUN pip install -r requirements.txt

#ADD Twitter ./Twitter
#ADD Data ./Data

CMD [ "python", "Twitter/WaitAnalyzer.py" ]
