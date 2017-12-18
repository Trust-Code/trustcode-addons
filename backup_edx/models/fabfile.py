# -*- coding: utf-8 -*-
# © 2017 Johny Chen Jy, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from fabric.api import *


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
    # Faz um novo backup atraves do mongodump
    run('sudo docker exec trustcode-edx mongodump -d edxapp -o /edx/app/edxapp/edx-platform/backup')
    # Comprime a pasta backup num arquivo tar.gz
    run('sudo docker exec trustcode-edx tar -czvf backup.tar.gz backup')
    # Transfere o arquivo zip do docker para a maquina remota
    run('sudo docker cp trustcode-edx:/edx/app/edxapp/edx-platform/backup.tar.gz ~/backup.tar.gz')
    # Transfere o arquivo zip da maquina remota para a maquina local
    get('~/backup.tar.gz', '~/backup.tar.gz')
    # Deleta pasta antiga de backup
    run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup')
    # Remove o zip antigo do backup
    run('sudo docker exec trustcode-edx rm backup.tar.gz')


# Define os parametros para a conecção na maquina na qual sera restaurada
# o backup
def host_to_restore():
    env.hosts = ['ubuntu@54.164.167.243']
    env.key_filename = '~/projetos/backup/edx-teste.pem'


def restore_backup():
    # Transfere o arquivo tar.gz(backup) para a maquina virtual
    put('~/backup.tar.gz', '/home/ubuntu/backup.tar.gz', use_sudo=True)
    # Transfere o arquivo do backup da maquina virtual para o docker
    run('sudo docker cp /home/ubuntu/backup.tar.gz trustcode-edx:/edx/app/edxapp/edx-platform/backup.tar.gz')
    # Descompacta o arquivo transferido
    run('sudo docker exec trustcode-edx tar -vzxf /edx/app/edxapp/edx-platform/backup.tar.gz')
    # Faz o restore atraves do mongorestore
    run('sudo docker exec trustcode-edx mongorestore --drop /edx/app/edxapp/edx-platform/backup')
    # Deleta o arquivo tar.gz antigo do backup dentro do docker da maquina
    # virtual
    run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup.tar.gz')
    # Deleta a pasta antiga de backup
    run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup')
