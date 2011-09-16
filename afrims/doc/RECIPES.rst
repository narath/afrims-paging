Recipes
=======
This is a list of recipes for getting stuff done with this project.

Most commonly used
=====
git add .
git commit
git flow feature finish simple_send

# aliases i use to setup the environ
rapaf
rapafv

./manage.py runrouter
./manage.py runserver
./manage.py

couchdb
~/start_postgres.sh
~/stop_postgres.sh

./manage.py test
./manage.py test afrims.apps.groups

# if you added another field to contacts, you can update the migrations with South
./manage.py schemamigration rapidsms --auto

Setting up
==========
Follow the setup from afrims

Fork Afrims
=======
Forked afrims
forked on github
git clone
cd
git remote add upstream https://github.com/afrims/afrims.git

cp localsettings.py.example localsettings.py

modify to use sqlite

# should be able to run it now

How to get an update from afrims
======
# i generally do this as part of a feature

git fetch upstream
git merge upstream/develop


Make sure you have virtualenv setup correctly
=====
virtualenv afrims-dev
source afrims-dev/bin/activate

Specific django version required
=========
1.2.4
gotcha: make sure you don't have it installed in your home dir, else pip won't override this
pip freeze

pip install django==1.2.4 --upgrade

Recommended dir structure
======
dev\
    (under git control)
    afrims-paging\
        afrims\
        requirements\
        services\

    afrims-dev\
        (virtual env settings here)

Setup ~/.bash_profile shortcuts:
======
alias rapafv='source ~/nSource/rapidsms/afrims-dev/bin/activate'
alias rapaf='cd ~/nSource/rapidsms/afrims-paging/afrims'
alias mg='./manage.py'

Setup Pycharm
========
Choose the correct python interpreter in project settings
i.e. the one from afrims-dev/bin

Note: it works well if you open the afrims as the dev dir
version control will not work (you need to use the command line for this)
but ./manage.py and running the server will work from here

if you run from the dev root i.e. afrims-paging/
then you will need to set, the DJANGO_SETTINGS environment var
and set the working directory to be afrims (so the db.sqlite3) will be shared

Get the latest version of rapidsms
=======
# you actually need the Dimagi version at this time

    pip uninstall rapidsms
    pip install git+https://github.com/dimagi/rapidsms.git#egg=RapidSMS


Setup the db
=====
./manage.py syncdb
./manage.py migrate

Add missing pips
=====
TODO: add to afrims requirements
pip install couchdbkit

Get the tests running
====
./manage.py tests
(or in PyCharm setup a Django test - this will run tests for you, has the benefit of hyperlinks back to your code)

Setting up CouchDB
====

http://wiki.apache.org/couchdb/Installing_on_OSX
brew install couchdb
# note: takes a long time - especially for the compile process

# on ubuntu
sudo apt-get install couchdb
# note: installs an older version but for dev purposes should be okay

# now create your database
http://127.0.0.1:5984/_utils
create couchlog
create rapidsms
# add user to rapidsms (don't worry about the passwd for your dev server
open rapidsms
click on security
in admin: ["rapid_user"]

# my staging server
http://192.168.1.204:5984/_utils/

# to use curl
HOST="http://192.168.1.204:5984"
curl -X GET $HOST/_all_dbs

# make sure couchlog is included in your settings:
COUCHDB_APPS=[
    'couchlog',
    'auditcare',
    ]

SETTING UP BACKENDS
========

To Setup kannel
======
# allow vm kannel to accept message from my host
sshb
# ssh into my virtual box with kannel installed

#BOXPATH=/usr/local/kannel/sbin
#PIDFILES=/var/run/kannel
#CONF=/etc/kannel/kannel.conf

# check to see that it is running
http://192.168.1.203:13000/status

# check to make sure you can send a test message
http://192.168.1.203:13013/cgi-bin/sendsms?username=opencellpager&password=PASSWORD&to=+16175551111&text=hello_world

# log files
sudo tail -f /tmp/kannel.log /tmp/smsbox.log /tmp/modem.log /tmp/access.log

# connect the modem, check it with screen /dev/ttyS0 (remember ^a-k exits)
screen /dev/ttyS0
# to reset the modem (if it is failing on CPIN)
AT+CFUN=1

# check that the process is running
ps ax | grep kannel

# edit config
sudo vim /etc/kannel/kannel.conf

# restart kannel
sudo /etc/init.d/kannel restart

# the best way to check that this is working is to:
127.0.0.1/admin
Add a contact e.g. narath
Add a connection: kannel, your google voice number here
Then using google voice - send a message to the server with either 'echo' or 'ping'
if all is working then it will send and receive