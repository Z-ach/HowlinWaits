# HowlinWaits

Wait time analyzer for [Howlin' Rays](https://howlinrays.com/)

Currently a WIP

## Getting Started
First, you will to authenticate with 3rd party APIs.  This project requires a secret key from the [DarkSky API](https://darksky.net/dev) and OAuth 1.0 information for the [Twitter API](https://developer.twitter.com/en/docs/basics/getting-started).  For Twitter, you will only need minimal read-only privelages.  Next, follow the [SecretTemplate.py](./Config/SecretTemplate.py) to populate `HowlinWaits/Config/Secret.py`.

You can run HowlinWaits with GPU training in Docker or with CPU training natively.

### Host (cpu)
```bash
cd HowlinWaits
pip3 install .
```
If Tensorflow 2.1 is not found, check that you are running Python 3.6.x 64 bit and that your pip is up to date.  To run using Tensorflow CPU just enter:
```
python3 WaitAnalayzer.py
```
### Docker (gpu)
Install [Docker](https://www.docker.com/) and [Nvidia-Docker](https://github.com/NVIDIA/nvidia-docker).

Run the following in the project's root directory to build the docker image: 
```bash
docker build -t howlin .
```
To run, simply execute `./run.sh`

### To do

#### Data Gathering:
- [X] Fetch tweets
- [X] Parse wait times from tweets
- [X] Insert data into sqlite3 DB

#### Data Analysis:
- [ ] Determine analysis method
- [ ] Implement analysis method

#### Publish 
- [ ] Create website displaying best times

