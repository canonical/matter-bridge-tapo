# Tapo Matter Bridge

## Install dependencies of the classic snap
```
sudo apt update
sudo apt install alsa mpg123
```

## Install
```
snap install --dangerous --classic ./matter-bridge-tapo-party-demo_0.1_amd64.snap
```

## Configure
```
sudo nano /var/snap/matter-bridge-tapo-party-demo/current/config.json
```

In the configuration file, the endpoint numbers 1 to 4 correspond to the matter endpoints, which can be passed to the `chip-tool` to control the devices. 

<!--
# Connect interfaces
```
snap connect matter-bridge-tapo-party-demo:avahi-control
```
-->

## Run
```
sudo snap start matter-bridge-tapo-party-demo
sudo snap logs -f matter-bridge-tapo-party-demo
```


### Control with Chip Tool

Commissioning:

```bash
chip-tool pairing ethernet 110 20202021 3840 192.168.1.111 5540
```

where:

-   `110` is the assigned node id
-   `20202021` is the pin code for the bridge app
-   `3840` is the discriminator id
-   `192.168.1.111` is the IP address of the host for the bridge
-   `5540` the the port for the bridge

Alternatively, to commission with discovery which works with DNS-SD:

```bash
chip-tool pairing onnetwork 110 20202021
```

Switching on/off:

```bash
chip-tool onoff toggle 110 1 # toggle is stateless and recommended
chip-tool onoff on 110 1
chip-tool onoff off 110 1
```

where:

-   `onoff` is the matter cluster name
-   `on`/`off`/`toggle` is the command name. The `toggle` command is RECOMMENDED
    because it is stateless. The bridge does not synchronize the actual state of
    devices.
-   `110` is the node id of the bridge app assigned during the commissioning
-   `1` is the endpoint of the configured device
