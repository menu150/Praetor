#!/bin/bash
cd /home/menu150/praetor
source venv/bin/activate
python feeds/white_house.py >> logs/white_house.log 2>&1
