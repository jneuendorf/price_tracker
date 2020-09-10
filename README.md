# price_tracker
Track prices (or virtually anything changes) of any web page


## Installation

### RaspberryPi

```bash
sudo apt-get update

# Python 3.8
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
tar xf Python-3.8.0.tar.xz
cd Python-3.8.0
./configure --enable-optimizations
make -j 4
sudo make altinstall

# Pipenv
pip3.8 install --user pipenv


# Native dependencies for lxml pip package
sudo apt-get install libxml2-dev libxslt-dev python-dev
sudo apt-get install python3-lxml python-lxml

pipenv install
```


## Project setup

- setup cron job
- migrate
- create super user
- run server using `pipenv run gunicorn --workers=4 --bind=0.0.0.0:8000 --daemon core.wsgi`
- configure pages to track
