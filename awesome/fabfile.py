import os, re
from datetime import datetime

from fabric.api import *

# server info
env.hosts = ['45.33.43.134:22']
env.user = 'hanker'
env.password = 'zhengzheng'
# server database info
db_user = 'www-data'
db_password = 'ThisIsPassWord'

_TAR_FILE = 'dist-awesome.tar.gz'
_REMOTE_TMP_TAR = '/tmp/%s' % _TAR_FILE
_REMOTE_BASE_DIR = '/srv/awesome'

_TAR_PHOTO = "dist-photo.tar.gz"
_REMOTE_PHOTO_TAR = "/tmp/%s" % _TAR_PHOTO

# Zip the target file, this function is executed locally
def build_www():
    includes = ['static', 'templates', 'transwarp', '*.py', 'robots.txt', '*.xml', '*.ico']
    # Ignore `test` file, invisible file, compied Python file
    excludes = ['test', '.*', '*.pyc', '*.pyo','photos']
    local('rm -f dist/%s' % _TAR_FILE)
    # lcd means `local cd`
    with lcd(os.path.abspath('www')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s'% _TAR_FILE]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

# Deploy the file into remote server
def deploy_www():
    newdir = 'www-%s' % datetime.now().strftime('%y-%m-%d_%H%M%S')
    # Delete the original file
    run('rm -f %s' % _REMOTE_TMP_TAR)
    # Upload the dist file
    put('dist/%s'%_TAR_FILE, _REMOTE_TMP_TAR)
    # Create new dir 
    with cd(_REMOTE_BASE_DIR):
        sudo('mkdir %s' % newdir)
    # Unzip to new dir
    with cd('%s/%s' % (_REMOTE_BASE_DIR, newdir)):
        sudo('tar -xzvf %s' % _REMOTE_TMP_TAR)
    # Reset soft link
    with cd(_REMOTE_BASE_DIR):
        sudo('rm -f www')
        sudo('ln -s %s www' % newdir)
        sudo('chown www-data:www-data www')
        sudo('chown -R www-data:www-data %s' % newdir)

    # Create soft link for photo
    with cd('%s/www/static/'%_REMOTE_BASE_DIR):
        sudo('ln -s /home/hanker/photos photos')
        sudo('chown -R www-data:www-data photos')

    # REBOOT python server and nginx server:
    with settings(warn_only=True):
        sudo('supervisorctl stop awesome')
        sudo('supervisorctl start awesome')
        sudo('/etc/init.d/nginx reload')

def build_photo():
    includes = ['*.jpg']
    excludes = ['raw', '*.py', '*.pyc']
    local('rm -f dist/%s' % _TAR_PHOTO)
    # lcd means `local cd`
    with lcd(os.path.abspath('photo')):
        cmd = ['tar', '--dereference', '-czvf', '../dist/%s'% _TAR_PHOTO]
        cmd.extend(['--exclude=\'%s\'' % ex for ex in excludes])
        cmd.extend(includes)
        local(' '.join(cmd))

def deploy_photo():
    # Delete the original file
    run('rm -f %s' % _REMOTE_PHOTO_TAR)
    # Upload the dist file
    put('dist/%s'%_TAR_PHOTO, _REMOTE_PHOTO_TAR)
    with cd("/home/hanker/photos"):
        sudo('tar -xzvf %s' % _REMOTE_PHOTO_TAR)

    with cd("/home/hanker/"):
        sudo('chown -R www-data:www-data photos')