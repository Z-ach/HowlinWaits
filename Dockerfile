FROM tensorflow/tensorflow:latest-gpu-py3
RUN mkdir -p /usr/home/app
WORKDIR /usr/home/app
ADD setup.py .
RUN pip install .

#ADD Twitter ./Twitter
#ADD Data ./Data

CMD [ "python", "WaitAnalyzer.py" ]
