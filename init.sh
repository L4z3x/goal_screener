#!/bin/bash

if [ -d "./goalenv" ];then
	echo 'INFO: dir goalenv exists skipping python venv installatio'
else
	pv=$(python --version || python3 --version)
	echo "PYTHON VERSION: $pv"
	
	echo -e "\e[1;32mINFO:\e[0m CREATING PYTHON VENV"
	python -m venv goalenv || python3 -m venv goalvenv

	echo -e "\e[1;32mINFO:\e[0m RUNNING goalvenv"
		
	echo -e "\e[1;32mINFO:\e[0m ACTIVATING goalvenv"
	
	VENV_PATH=$(python -c 'import os; print(os.getcwd())')
	echo $VENV_PATH
	
	source "$VENV_PATH/goalenv/bin/activate"

	echo -e "\e[1;33m NOTE:\e[0m IT'S BETTER TO MAKE AN ALIAS FOR THE ACTIVATION CMD COPY THIS TO YOUR ~/.bashrc FILE alias goalvenv="source $VENV_PATH/bin/activate""
	
	echo -e "\e[1;32m INFO:\e[0m INSTALLING Dependencies: pillow Pyqt"

	pip install -r requirement.txt

fi
# add the data file
echo -e "\e[1;32m INFO:\e[0m CREATING ./assets/Quests.json FILE FOR DATA" 
touch ./assets/Quest.json
chmod 666 ./assets/Quest.json
# run the app
echo -e "\e[1;32m INFO:\e[0m STARTING goal_Screener. ENJOY :)"
python app.py
