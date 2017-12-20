# -*- coding: utf-8 -*-
# © 2017 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

_logger = logging.getLogger(__name__)

try:
    from fabric.api import local, env, run, get, put
except ImportError:
    _logger.debug(u'Cannot import fabric')


def backup():
    local('fab host_to_backup get_backup -f \
~/projetos/odoo11/trustcode-addons/backup_edx/models/fabfile.py')


def restore():
    local('fab host_to_restore restore_backup -f \
~/projetos/odoo11/trustcode-addons/backup_edx/models/fabfile.py')


# Define o endereço e a key do host a ser feito o backup.
def host_to_backup():
    env.hosts = ['ubuntu@34.227.148.187']
    env.key_filename = '~/projetos/backup/edx-teste.pem'


# Método na qual executa as funções do backup
def get_backup():
    # Faz um novo backup atraves do mongodump (Parte 1/2)
    run('sudo docker exec trustcode-edx mongodump -d edxapp -o \
/edx/app/edxapp/edx-platform/backup')
    # Backup do mysql (Parte 2/2)
    run('sudo docker exec trustcode-edx mysqldump -u root edxapp > edx.sql')
    # Transfere o folder do docker para a maquina remota
    run('sudo docker cp trustcode-edx:/edx/app/edxapp/edx-platform/backup \
~/backup')
    # Comprime a pasta backup num arquivo tar.gz
    run('tar -czvf backup.tar.gz edx.sql backup')
    # Transfere o arquivo zip da maquina remota para a maquina local
    get('~/backup.tar.gz', '~/backup.tar.gz')

    # Remove todos os arquivos remanescentes
    run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/\
backup')
    run('sudo rm -r backup')
    run('sudo rm -f edx.sql')
    run('sudo rm -f backup.tar.gz')


# Define os parametros para a conecção na maquina na qual sera restaurada
# o backup
def host_to_restore():
    env.hosts = ['ubuntu@54.164.167.243']
    env.key_filename = '~/projetos/backup/edx-teste.pem'


def restore_backup():
    # Transfere o arquivo tar.gz(backup) para a maquina virtual
    put('~/backup.tar.gz', '/home/ubuntu/backup.tar.gz', use_sudo=True)
    # Descompacta o arquivo transferido
    run('tar -vzxf backup.tar.gz')
    # Transfere o arquivo do backup da maquina virtual para o docker
    run('sudo docker cp /home/ubuntu/backup trustcode-edx:/edx/app/edxapp/\
edx-platform/backup')
    # Faz o restore atraves do mongorestore (1/2)
    run('sudo docker exec trustcode-edx mongorestore --drop /edx/app/edxapp/\
edx-platform/backup')
    # Faz restore do mysql (2/2)
    run('sudo docker exec -i trustcode-edx /usr/bin/mysql -u root edxapp < \
edx.sql')

    # Deleta os arquivos remanescentes
    run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/\
backup')
    run('sudo rm -r edx.sql')
    run('sudo rm -r backup')
    run('sudo rm -f backup.tar.gz')
