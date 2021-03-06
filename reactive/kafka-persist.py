import os
from charmhelpers.core import hookenv, unitdata
from charmhelpers.core.hookenv import status_set, log
from charms.reactive import when, when_not, set_state, remove_state, when_none
from charms.layer.kafkahelper import brokers_as_string


@when_not('kafka.configured')
def waiting_for_kafka():
    status_set('blocked', 'Waiting for Kafka relation')


@when_none('mongodb.available', 'rabbitmq.connected')  # Add all database states
def waiting_for_database():
    status_set('blocked', 'Waiting for datastore relation')


@when('database.configured')
@when_none('mongodb.available', 'rabbitmq.connected')  # Add all database states
def database_removed():
    hookenv.log('Database relation removed')
    remove_state('kafkaingestion.installed')
    remove_state('database.configured')


@when('mongodb.available')
def mongodb_connected(mongodb):
    hookenv.log('Mongodb connected')
    configure_env('datastore_type', 'mongodb')  # Should be set by every connected db
    configure_env('mongodb_conn', mongodb.connection_string())
    set_state('database.configured')   # Should be set by every connected db


@when('rabbitmq.connected')
@when_not('rabbitmq.available')
def setup_rabbitmq(rabbitmq):
    rabbitmq.request_access('persist', '/persist')
    status_set('waiting', 'Waiting on RabbitMQ to configure vhost')


@when('rabbitmq.available')
def configure_rabbitmq(rabbitmq):
    configure_env('datastore_type', 'rabbitmq')
    configure_env('rabbitmq_username', rabbitmq.username())
    configure_env('rabbitmq_password', rabbitmq.password())
    configure_env('rabbitmq_vhost', rabbitmq.vhost())
    configure_env('rabbitmq_host', rabbitmq.private_address())
    configure_env('rabbitmq_port', 5672)
    set_state('database.configured')


@when('dockerhost.available', 'kafka.configured', 'database.configured')
@when_not('kafkaingestion.installed')
def start_ingestion(dh_relation):
    if not hookenv.config()['topics']:
        status_set('blocked', 'Waiting for topics')
        return
    configure_env('kafka', brokers_as_string(' '))
    configure_env('topics', hookenv.config()['topics'])
    configure_env('groupid', os.environ['JUJU_UNIT_NAME'].split('/')[0])
    status_set('maintenance', 'Sending container request to docker host')
    set_state('docker-image.start')
    set_state('kafkaingestion.installed')


@when('config.changed.topics')
def config_changed_topics():
    remove_state('config.changed.topics')
    remove_state('kafkaingestion.installed')


@when('config.changed.ports')
def config_changed_ports():
    remove_state('config.changed.ports')
    remove_state('kafkaingestion.installed')


@when('kafkaingestion.installed')
@when_not('dockerhost.available')
def dockerhost_removed():
    hookenv.log('Dockerhost removed')
    unitdata.kv().set('containers', {})
    remove_state('kafkaingestion.installed')


def configure_env(key, value):
    env = unitdata.kv().get('docker-image-env', {})
    env[key] = value
    unitdata.kv().set('docker-image-env', env)
