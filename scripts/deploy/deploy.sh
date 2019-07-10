#!/bin/bash

set -e;
set -x;

echo "Agregando clave SSH"
eval "$(ssh-agent -s)"
ssh-add /tmp/build\+infra@travis-ci.org

# Nota: Las variables no definidas aqui deben ser seteadas en ./variables.sh

echo "Ejecutando comando de instalación..."
ssh $DEPLOY_TARGET_USERNAME@$DEPLOY_TARGET_IP -p$DEPLOY_TARGET_SSH_PORT "\
    cd /home/$DEPLOY_TARGET_USERNAME/infra.datos.gob.ar-deploy &&\
    git pull &&\
    source ./env/bin/activate &&\
    ansible-playbook -i /home/$DEPLOY_TARGET_USERNAME/infra.datos.gob.ar-deploy/inventories/$DEPLOY_ENVIRONMENT/hosts --extra-vars='checkout_branch=$DEPLOY_REVISION' --vault-password-file $DEPLOY_TARGET_VAULT_PASS_FILE --extra-vars='ansible_sudo_pass=$DEPLOY_TARGET_SUDO_PASS' playbook.yml -vv"
