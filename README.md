# Safe-Signup
A signup and login page with a built in email verification.

# How to use?

## Install python

**Linux** 

```sudo apt install python3```

**Windows**

```irm https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe -OutFile python.exe; Start-Process python.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; Remove-Item python.exe```

## Install extentions

**Linux**

```python3 -m pip install -r extentions.txt```

**Windows**

```pip install -r extentions.txt```

## Setup

Open app.py with notepad or nano and change the ```app.secret_key``` to something secure.
Then find the ```conn = mysql.connector.connect``` section and change the "database =" to your MySQL database name. Example: ```database=s1_userdata```
Now save and close the file.

Then open the file named ```emsdf.ef``` and enter in your mail smtp server credentials, this should be done in the format of ```EMAILSERVER:PORT:TLS:USER:PASSWORD:SENDFROM```

Now open the file named ```user.data``` and enter in your MySQL server credentials, this is required to save user data.
This should be done in the format of ```IP:PORT:USERNAME:PASSWORD```

## Run the server

**Linux**

```python3 app.py```

**Windows**

```python app.py```

# Features

**1**. Very Fast

**2**. Open Source

**3**. Easy to use

**4**. Customisable

**5**. Secure
