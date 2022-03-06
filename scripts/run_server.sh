#!/bin/bash

cd app || exit
su -m app -c "python3.8 app.py"