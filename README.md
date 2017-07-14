# Layer-kafka-persist

This layer creates a kafka -> data store stream.

Supported data stores:
- [Mongodb](https://jujucharms.com/mongodb/)

Layers required to build this charm:
 - [kafka-helper](https://github.com/tengu-team/layer-kafka-helper)
 - [docker-image](https://github.com/tengu-team/layer-docker-image)

# How to use
Deploy a [docker-host](https://github.com/tengu-team/layer-docker-host) based charm.
Kubernetes is also supported when using the [kubernetes-deployer](https://github.com/tengu-team/layer-kubernetes-deployer) layer.
```
juju deploy cs:~tengu-team/docker-host
```
Deploy the kafka-persist charm.
```
juju deploy ./kafka-persist
```
Add relations to Kafka, the docker engine and a supported data store.
```
juju add-relation kafka-persist kafka
juju add-relation kafka-persist mongodb
juju add-relation kafka-persist kubernetes-master
```
Set the topics to be persisted.
```
juju config kafka-persist "topics=topic.1"
```
Check the deployment status.
```
watch -c juju status --color
```


# Important notes

## Kafka behaviour
- There are currently no options to set the offset on the Kafka topic.
**The charms unit name is used (minus the unit number) as consumer group and will
default to the latest available offset.**

## Mongodb behaviour
- In Mongodb, a database with the name `cot` is created.
For every subscribed topic, a collection with the same name is created.

## Authors

This software was created in the [IBCN research group](https://www.ibcn.intec.ugent.be/) of [Ghent University](https://www.ugent.be/en) in Belgium. This software is used in [Tengu](http://tengu.intec.ugent.be), a project that aims to make experimenting with data frameworks and tools as easy as possible.

 - Sander Borny <sander.borny@ugent.be>