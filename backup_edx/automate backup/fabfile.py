from fabric.api import local, run, env, get, put
from odoo import models


def backup():
    local('fab host_to_backup get_backup')


def restore():
    local('fab host_to_restore restore_backup')


# Define o endereço e a key do host a ser feito o backup.
def host_to_backup():
    env.hosts = ['ubuntu@34.227.148.187']
    env.key_filename = '~/projetos/backup/edx-teste.pem'


# Método na qual executa as funções do backup
def get_backup():
    # Deleta pasta antiga de backup
    try:
        run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup')
    except Exception as e:
        print(e)
    # Faz um novo backup atraves do mongodump
    run('sudo docker exec trustcode-edx mongodump -d edxapp -o /edx/app/edxapp/edx-platform/backup')
    # Remove o zip antigo do backup
    try:
        run('sudo docker exec trustcode-edx rm backup.tar.gz')
    except Exception as e:
        print(e)
    # Comprime a pasta backup num arquivo tar.gz
    run('sudo docker exec trustcode-edx tar -czvf backup.tar.gz backup')
    # Transfere o arquivo zip do docker para a maquina remota
    run('sudo docker cp trustcode-edx:/edx/app/edxapp/edx-platform/backup.tar.gz ~/backup.tar.gz')
    # Transfere o arquivo zip da maquina remota para a maquina local
    get('~/backup.tar.gz', '~/backup.tar.gz')


# Define os parametros para a conecção na maquina na qual sera restaurada o backup
def host_to_restore():
    env.hosts = ['ubuntu@54.164.167.243']
    env.key_filename = '~/projetos/backup/edx-teste.pem'


def restore_backup():
    # Transfere o arquivo tar.gz(backup) para a maquina virtual
    put('~/backup.tar.gz', '/home/ubuntu/backup.tar.gz', use_sudo=True)
    # Deleta o arquivo tar.gz antigo do backup dentro do docker da maquina virtual
    try:
        run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup.tar.gz')
    except Exception as e:
        print(e)
    # Transfere o arquivo do backup da maquina virtual para o docker
    run('sudo docker cp /home/ubuntu/backup.tar.gz trustcode-edx:/edx/app/edxapp/edx-platform/backup.tar.gz')
    # Deleta a pasta antiga de backup
    try:
        run('sudo docker exec trustcode-edx rm -R /edx/app/edxapp/edx-platform/backup')
    except Exception as e:
        print(e)
    # Descompacta o arquivo transferido
    run('sudo docker exec trustcode-edx tar -vzxf /edx/app/edxapp/edx-platform/backup.tar.gz')
    # Faz o restore atraves do mongorestore
    run('sudo docker exec trustcode-edx mongorestore --drop /edx/app/edxapp/edx-platform/backup')
