#!/bin/bash

name_post_fix=( "one" "two" )

i=0
for post_fix in ${name_post_fix[@]}; do
  sudo docker run -d --hostname rabbit-$post_fix --name some-rabbit-$post_fix -e RABBITMQ_ERLANG_COOKIE='SECRETTOKEN' rabbitmq:3-management
  sudo docker cp rabbitmq.conf some-rabbit-$post_fix:/etc/rabbitmq/rabbitmq.conf

  sudo docker exec -d some-rabbit-$post_fix mkdir /etc/rabbitmq/tls
  sudo docker cp ../testca/cacert.pem some-rabbit-$post_fix:/etc/rabbitmq/tls/cacert.pem
  sudo docker cp ../server/cert.pem some-rabbit-$post_fix:/etc/rabbitmq/tls/cert.pem
  sudo docker cp ../server/key.pem some-rabbit-$post_fix:/etc/rabbitmq/tls/key.pem

  echo "some-rabbit-$post_fix" >> running_hosts

  i=$(($i + 1))
done

echo -n "Waiting for nodes to start"

for post_fix in ${name_post_fix[@]}; do
  res=1

  while [ $res -ne 0 ]; do
    sleep 1
    echo -n "."
    sudo docker exec some-rabbit-$post_fix rabbitmqctl status | grep rabbitmq_management, > /dev/null
    res=$(sudo docker exec some-rabbit-one echo $?)
  done
done

echo ""

for post_fix in ${name_post_fix[@]}; do
  if [[ $post_fix = "one" ]]; then
    sudo docker exec some-rabbit-one /bin/sh -c "echo \"172.17.0.3\trabbit-two\" >> /etc/hosts"
    sudo docker exec some-rabbit-one rabbitmqctl set_policy ha-all "" '{"ha-mode":"all","ha-sync-mode":"automatic"}'
  elif [[ $post_fix = "two" ]]; then
    sudo docker exec some-rabbit-two /bin/sh -c "echo \"172.17.0.2\trabbit-one\" >> /etc/hosts"
    sudo docker exec some-rabbit-two rabbitmqctl stop_app
    sudo docker exec some-rabbit-two rabbitmqctl join_cluster rabbit@rabbit-one
    sudo docker exec some-rabbit-two rabbitmqctl start_app
  fi
done

