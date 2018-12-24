# CatalogApp

CatalogApp is web site server in python language that That browse a group of items,
with the ability to modify, delete, or add new items to this group.

## Install and Run
to running program:
- download and unzip 'catalogitem_prog', then cd into that folder.
- Create your OAuth Client ID in the Google APIs:
   - Go to your app's page in the [Google APIs Console](https://console.developers.google.com/apis)
   - Choose Credentials from the menu on the left.
   - Create an OAuth Client ID.
   - When you're presented with a list of application types, choose Web application.
   - You can then edit setting and add `http://localhost:8000` to JAVASCRIPT ORIGIN and
    `http://localhost:8000/login` to REDIRECT URIS.
   - You will then be able to get the client ID and client secret.
   - download the client secret as a JSON data file once you have created it and rename it ot `client_secrets.json`
- copy `client_secrets.json` to 'catalogitem_prog' folder.
- Find and open the **login.html** file and replace `CLIENT_ID` with your own.
- run program as following 
 
~~~
$ python catalogapp.py
~~~
But Before you run this program, there are dependencies and resourse, so following this instruction:

#### 1- Install VirtualBox
 VirtualBox is the software that actually runs the virtual machine. You can download it from virtualbox.org, [here](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1). Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.
 
  **Ubuntu users**: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center instead. Due to a reported bug, installing VirtualBox from the site may uninstall other software you need.[1]
 
#### 2- Install Vagrant
 Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem. Download it from [vagrantup.com](https://www.vagrantup.com/downloads.html). Install the version for your operating system.
 
 **Windows users**: The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.[2]

 after this,, you need download configuration VM that configer Ubuntu to install postgresql, python and other dependencies.
 You can download and unzip this file: [FSND-Virtual-Machine.zip](https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip) [3]  This will give you a directory called FSND-Virtual-Machine. 
 
From your terminal, change directory to the vagrant subdirectory that located in FSND-Virtual-Machine directory, run the command `vagrant up`. This will cause Vagrant to download the Linux operating system and install it. after that done, you can run command `vagrant ssh` to log in VM.[4]

## JSON API structure
- `http://localhost:8000/catalog/json`:
   This brings data of all categories and items.
- `http://localhost:8000/catalog/category-id/json`:
   This brings data of category with _category-id_ ID and its items.
- `http://localhost:8000/catalog/category-id/item-id/json`:
   This brings data for item with _item-id_ ID.

## Reference
   - [1][2][3][4][5] Udacity.com lessons.
   - Udacity classroom.
   - [How to Writing READMEs](https://classroom.udacity.com/courses/ud777) lesson, Udacity website.
   - [https://www.w3schools.com](https://www.w3schools.com)
 
