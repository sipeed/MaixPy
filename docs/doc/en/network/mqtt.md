---
title: Using MQTT with MaixPy MaixCAM for Message Subscription and Publishing
---

## MQTT Introduction

MQTT allows for quick and easy real-time communication using a publish-subscribe model.

System components:
* **MQTT Server (broker):** Responsible for forwarding messages.
* **MQTT Clients:** Subscribe to topics from the server, receive messages, and publish messages to specific topics on the server.

Communication process:
* Clients connect to the MQTT server.
* Clients subscribe to topics they are interested in, such as `topic1`.
* When other clients or the server publish information on the `topic1` topic, it is pushed to the subscribing clients in real time.
* Clients can also actively publish messages to specific topics. All clients subscribed to that topic will receive the messages. For example, if a client publishes a message to `topic1`, all clients subscribed to `topic1` will receive it, including the publishing client itself.

## Using MQTT in MaixPy MaixCAM

The `paho-mqtt` module can be used for this purpose. You can look up the usage of `paho-mqtt` online or refer to the examples in the [MaixPy/examples](https://github.com/sipeed/MaixPy/tree/main/examples/network) repository.

If you are using an older system, you might need to manually install the `paho-mqtt` package. Installation instructions can be found in the [Adding Extra Python Packages](../basic/python_pkgs.md) guide.


