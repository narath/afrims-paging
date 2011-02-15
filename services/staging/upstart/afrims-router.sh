# This script will start/stop the TrialConnect django server running via a management command
# This script assumes gunicorn and gevent are installed and configured for your django project
# Copy this script and name it the service you want in your ubuntu system to /etc/init/
description "start and stop the django_project"

# configuration variables.
# You'll want to change these as needed
env PROJECT_NAME=afrims
env DJANGO_HOME=/home/afrims/www/staging/code_root/afrims #where manage.py is
env DJANGO_PORT=9001
env DJANGO_HOST=0.0.0.0 # bind to 0.0.0.0 or other port where needed
env DJANGO_VIRTUALENV=/home/afrims/www/staging/python_env

# tell upstart we're creating a daemon
# upstart manages PID creation for you.
expect fork

start on started afrims
stop on stopped afrims
pre-start script
        chdir $DJANGO_HOME
end script

script
        # Note, we're using the virtualenv's python interpreter.  Calling source/workon doesn't work here, so just call the ENV's executable instead.
         exec $DJANGO_VIRTUALENV/bin/python $DJANGO_HOME/manage.py runrouter &
        #exec $DJANGO_VIRTUALENV/bin/python $DJANGO_HOME/manage.py run_gunicorn $DJANGO_HOST:$DJANGO_PORT --preload -w 3 --log-level debug -p $DJANGO_HOME/$PROJECT_NAME.pid  -k gevent &

end script
