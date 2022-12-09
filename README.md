# Tapo Matter Bridge

## Install
```
snap install --dangerous --devmode ./lighting-tapo_0.1_amd64.snap
```

## Configure
```
sudo cp /snap/lighting-tapo/current/etc/config.json.example /var/snap/lighting-tapo/current/config.json
sudo cp /snap/lighting-tapo/current/etc/disco.mp3 /var/snap/lighting-tapo/current/
```

## Run
```
snap start lighting-tapo
snap logs -f lighting-tapo
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
chip-tool onoff on 110 1
chip-tool onoff off 110 1
chip-tool onoff toggle 110 1
```
