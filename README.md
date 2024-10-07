# Gaol_Screener
a simple python app built with pyqt and pillow to boost your production 
by visualzing your goals/quests in the home background and tracking them
(Inspired by AC valhalla quest menu BTW)
 ## Note
 recommanded image size : 3840*2160
 for linux machines, this app will work only on GTK-based DE (desktop enviroments)
 ## Example
 if this is your desktop background:
 
 ![Logo](./example/background.png)
 
 then it will look like this, note that your background img should be clean to make good effect.
 (the little green icon points to the tracked quest)
 
 ![Logo](./example/output.png)
 
 ## Start
 clone the repo: 
  	
   	git clone https://github.com/L4z3x/goal_screener/
 
 if you use Linux (gtk-based DE)   
 execute the script init.sh:
 	
  	sudo ./init.sh
 to run the app:
 	
  	sudo python app.py

for Windows
create the file ./assets/Quest.json

    cd ./assets/
    copy con Quest.json

then create py venv and activate it

    python -m venv goalenv
    .\goalenv\Scripts\activate
if you want to deactivate it, just type "deactivate"

install pillow and Pyqt

    pip install -r requirement.txt   

now you can run the app from (.\"windows app"\goalScreener)
and don't forget to create a symlink (shortcut) for easy access.
