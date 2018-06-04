# HelpBot

## Introduction

HelpBot is a primitive chatbot designed to answer technical questions in Facebook chats. All packages used are listed in the respective requirements.txt file.

## Installation

To install HelpBot, one must simply use the Python Package Manager, pip as shown below. Warning: this code has only been tested using python 2. Porting to python 3 should be trivial if need be.

```sh
pip install -r requirements.txt
# Alternative commands (only need to run one) are listed below
sudo pip install -r requirements.txt
pip install --user requirements.txt
```

Note: this code has been tested using [virtualenv](https://virtualenv.pypa.io/en/stable/).

## Configuration

A .env file is required to configure this project. An example of how to make a .env file for this program is listed below

Example of how to make a .env in cmd/terminal of your computer
```sh
# Linux/Max: note you may use any text editor of your preference to
# make the file named .env in the directory as the program
touch .env
nano .env
# Windows
notepad.exe .env
```

Example file written using favorite text editor
```sh
FB_USER=<your facebook email>
FB_PASSWORD=<your facebook password>
# This bottom value is optional, makes script startup time on avergae faster
PICKLE_FILENAME=classifier_pickle
```

## TODOS

* Make code forward compatible with Python 3
* Improve classification model and build data sets directly from Stack Overflow
* Look into tfidf, tnse, and ngrams
* May consider an actual nn for this
