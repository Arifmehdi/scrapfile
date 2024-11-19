****************************************************** START Install Package ****************************************************************
01. check python 
--> python --version

02. pip install
--> py -m pip install --upgrade pip             ###update pip
--> python.exe -m pip install --upgrade pip     ###suggested by command line 

03. virtual env (venv) install
--> py -m venv venv

04. activate env
--> .\venv\Scripts\Activate

05. if need purge 
--> pip cache purge

****************************************************** END Install Package ****************************************************************



****************************************************** START Individual Package ****************************************************************
06. install selenium
--> pip install selenium

07. install website_manager
--> pip install webdriver_manager

08. install panda and mysql connector
--> pip install pandas mysql-connector-python

09. pip install requests
--> pip install requests

10. install beautifulsoup
-->pip install beautifulsoup4

11 install pytesseract
--> pip install selenium pillow pytesseract

****************************************************** END Individual Package ****************************************************************

****************************************************** START Windows exe file ****************************************************************
01. Install PyInstaller: Make sure you have PyInstaller installed. You can install it via pip:

## use just two line code 

--> pip install pyinstaller

02. Create the Executable: Open a terminal or command prompt in the directory where your script is located and run the following command:

--> pyinstaller --onefile --windowed your_script.py
******************************************************  END Windows exe file  ****************************************************************