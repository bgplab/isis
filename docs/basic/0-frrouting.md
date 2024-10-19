# Configuring IS-IS on FRRouting

Most networking devices[^CL] use a configuration command line interface (CLI) to interact with the end-user. The CLI usually provides **show** commands to inspect the state of the device and a configuration mode that allows the user to configure the device.

[^CL]: Including devices based on Linux like Arista EOS, Cisco Nexus OS, or Nokia SR Linux

FRRouting is different. It's a suite of application-layer daemons running on Linux. Linux shell is used as the initial CLI. To configure a device that uses FRRouting without an extra CLI wrapper (like VyOS), you usually have to:

* Use standard Linux tools like *ifupdown* to configure the interfaces;
* [Edit FRRouting configuration files](#daemon) to start routing protocol daemons
* [Start FRRouting configuration shell](#vtysh) from the Linux CLI.

The Linux interfaces and IP addresses will be configured automatically if you start the IS-IS labs with the **netlab up** command. You will have to start the routing protocol daemons in the initial lab exercises if you plan to use FRRouting within virtual machines as the user routers, and you might have to execute **show** commands on Cumulus Linux or FRRouting acting as the external routers. You'll practice both in this lab exercise.

![Lab topology](topology-frrouting.png)

## Start the Lab

You can start the lab [on your own lab infrastructure](../1-setup.md) or in [GitHub Codespaces](https://github.com/codespaces/new/bgplab/isis) ([more details](https://bgplabs.net/4-codespaces/)):

* Change directory to `basic/0-frrouting`
* Execute **netlab up** to start a lab with two FRRouting virtual machines or containers (depending on your lab setup). R2 is preconfigured to run IS-IS; if you're using virtual machines, you might have to enable the IS-IS daemon on R1.
* Log into the devices (`r1` and `r2`) with the **netlab connect** command.

## Start the IS-IS Daemon {#daemon}

Most network devices start routing daemons when you configure them through the configuration CLI or API. FRRouting is different. To start a routing daemon, you must enable the desired routing daemons in a configuration file and restart the top-level FRRouting process.

You can check the FRR daemon processes running on your virtual machines with the `sudo systemctl status frr.service` command. It displays the running FRR daemons and the recent FRR logging messages, for example[^DEV]:

[^DEV]: The printout details depend on the Linux and FRR versions, but you'll always be able to determine whether the IS-IS process is running.

```bash
r2(bash)#sudo systemctl status frr.service
● frr.service - FRRouting
     Loaded: loaded (/lib/systemd/system/frr.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2024-07-17 17:09:27 UTC; 37s ago
       Docs: https://frrouting.readthedocs.io/en/latest/setup.html
    Process: 4051 ExecStart=/usr/lib/frr/frrinit.sh start (code=exited, status=0/SUCCESS)
   Main PID: 4071 (watchfrr)
     Status: "FRR Operational"
      Tasks: 1 (limit: 1049)
     Memory: 1.8M
     CGroup: /system.slice/frr.service
             └─4071 /usr/lib/frr/watchfrr -d -F traditional zebra mgmtd isisd staticd

Jul 17 17:09:27 r2 systemd[1]: Starting FRRouting...
Jul 17 17:09:27 r2 frrinit.sh[4051]:  * Starting watchfrr with command: '  /usr/lib/frr/watchfrr  -d  -F traditional   zebra mgmtd >
Jul 17 17:09:27 r2 watchfrr[4071]: [T83RR-8SM5G] watchfrr 10.0.1 starting: vty@0
Jul 17 17:09:27 r2 watchfrr[4071]: [QDG3Y-BY5TN] zebra state -> up : connect succeeded
Jul 17 17:09:27 r2 watchfrr[4071]: [QDG3Y-BY5TN] mgmtd state -> up : connect succeeded
Jul 17 17:09:27 r2 watchfrr[4071]: [QDG3Y-BY5TN] isisd state -> up : connect succeeded
Jul 17 17:09:27 r2 watchfrr[4071]: [QDG3Y-BY5TN] staticd state -> up : connect succeeded
Jul 17 17:09:27 r2 watchfrr[4071]: [KWE5Q-QNGFC] all daemons up, doing startup-complete notify
Jul 17 17:09:27 r2 frrinit.sh[4051]:  * Started watchfrr
Jul 17 17:09:27 r2 systemd[1]: Started FRRouting.
```

You cannot use the same command in FRRouting containers as they don't use `systemd`. The easiest way to find daemons in FRRouting containers is to use the `ps -ef|grep frr` command[^UE]. This is the printout you could get when the IS-IS daemon is already running:

[^UE]: You can use the same command with FRRouting running in a virtual machine.

```bash
    1 root      0:00 /sbin/tini -- /usr/lib/frr/docker-start
    7 root      0:00 {docker-start} /bin/bash /usr/lib/frr/docker-start
   15 root      0:00 /usr/lib/frr/watchfrr zebra mgmtd isisd staticd
   25 frr       0:00 /usr/lib/frr/zebra -d -F datacenter -A 127.0.0.1 -s 90000000
   30 frr       0:00 /usr/lib/frr/mgmtd -d -F datacenter
   32 frr       0:00 /usr/lib/frr/isisd -d -F datacenter -A 127.0.0.1
   35 frr       0:00 /usr/lib/frr/staticd -d -F datacenter -A 127.0.0.1
  366 root      0:00 grep frr
```

The list of FRRouting daemons you want to enable is stored in the `/etc/frr/daemons` file. To enable the FRRouting IS-IS daemon, you have to:

* Add the `isisd=yes` line to the `/etc/frr/daemons` file[^FRMD].
* Restart FRRouting with the `sudo systemctl restart frr.service` command (see also: [using sudo](#sudo))

[^FRMD]: See [Configuring FRRouting](https://docs.nvidia.com/networking-ethernet-software/cumulus-linux-41/Layer-3/Configuring-FRRouting/) Cumulus Linux documentation for more details.
    
!!! warning
    * You cannot change the FRR daemons in FRR containers. Restarting FRR would kill the container. _netlab_ takes care of that and enables all the daemons necessary to complete the lab exercises.
    * Restarting FRR daemons wipes out the current (running) configuration. If you want to retain it, save it to the startup configuration with the _vtysh_ **write** command.
    * The **write** command saves the running configuration (that you can inspect with **show running-config**) into the `/etc/frr/frr.conf` file. However, the **show startup-config**[^CLSC] does not display the content of that file. Exit _vtysh_ and use the **more /etc/frr/frr.conf** command[^MNS] to inspect it.

[^CLSC]: At least on FRRouting version 9.1 and earlier

[^MNS]: You [might](#sudo) have to prefix it with **sudo**

You could add the required line to the FRRouting daemons file with any text editor[^TE] or use the following trick:

* Use **sudo bash** to start another Linux shell as the root user
* Use the **echo** command with output redirection to add a line to the `/etc/frr/daemons` file.

[^TE]: `vi` is available in Cumulus Linux containers. `vi` and `nano` are available in Cumulus Linux and FRR virtual machines.


```bash
rtr(bash)#sudo bash
root@rtr:/# echo 'isis=yes' >>/etc/frr/daemons
root@rtr:/# exit
```

After enabling the IS-IS daemon and restarting FRR, you should see the `isisd` process in the `ps -ef` printout or the IS-IS daemon mentioned in the `sudo systemctl status frr.service` printout.

## Work with the FRRouting CLI {#vtysh}

FRRouting suite includes a virtual shell (*vtysh*) closely resembling industry-standard CLI[^ISC]. It has to be started from the Linux command line with the vtysh command. The `vtysh` CLI has to run as the root user unless you change the FRR-related permissions to allow a regular user to use it. The usual command to start the _vtysh_ is thus `sudo vtysh` (but see also [To Sudo Or Not to Sudo](#sudo)).

[^ISC]: An euphemism for *Cisco IOS CLI* that is used when you try to avoid nasty encounters with Cisco's legal team.

```bash
r2(bash)#sudo vtysh

Hello, this is FRRouting (version 9.1_git).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

r2#
```

Once you started _vtysh_, you can execute **show** commands to inspect the device state, for example:

```bash
r2(bash)#sudo vtysh

Hello, this is FRRouting (version 9.1_git).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

r2# show ip route
Codes: K - kernel route, C - connected, S - static, R - RIP,
       O - OSPF, I - IS-IS, B - BGP, E - EIGRP, N - NHRP,
       T - Table, v - VNC, V - VNC-Direct, A - Babel, F - PBR,
       f - OpenFabric,
       > - selected route, * - FIB route, q - queued, r - rejected, b - backup
       t - trapped, o - offload failure

C>* 10.0.0.2/32 is directly connected, lo, 00:02:26
C>* 10.1.0.0/30 is directly connected, eth1, 00:02:26
```

You can also use the `--show` option of the **netlab connect** command to execute a single command on a FRR/Cumulus Linux device[^UQ]. For example, to inspect the IS-IS topology database, use `netlab connect --show isis database`:

```
$ netlab connect r2 --show isis database
Connecting to container clab-frrouting-r2, executing vtysh -c "show isis database"
Area Gandalf:
IS-IS Level-2 link-state database:
LSP ID                  PduLen  SeqNumber   Chksum  Holdtime  ATT/P/OL
r2.00-00             *     81   0x00000001  0xec86    1489    0/0/0
    1 LSPs
```
    
To configure FRRouting daemons, use the **configure** _vtysh_ command and enter configuration commands similar to those you'd use on Cisco IOS or Arista EOS:

```
r2(bash)#vtysh

Hello, this is FRRouting (version 9.1_git).
Copyright 1996-2005 Kunihiro Ishiguro, et al.

r2# configure
r2(config)# router isis Gandalf
r2(config-router)#
```

## To Sudo Or Not to Sudo {#sudo}

The _vtysh_ usually has to run as the **root** user, so you should start it with the `sudo vtysh` command. Unfortunately, things are never as simple as they look in the Linux world:

* When using SSH, you log into Cumulus Linux or FRRouting virtual machines as a regular user (user *vagrant* in _netlab_-created labs) and have to use the `sudo` command to start _vtysh_.
* Cumulus Linux and FRR containers run as the **root** user, and you connect to them as the **root** user with the `docker exec` or `netlab connect` commands[^WIDUW]. When working with containers, you can start _vtysh_ without using the `sudo` command.
* You can execute `sudo vtysh` as a root user on Cumulus Linux containers but not within an FRR container. The FRR container does not include the `sudo` command.

[^WIDUW]: When in doubt, use the **whoami** command.

**Long story short:**

* Use `sudo vtysh` whenever possible to burn it into your muscle memory.
* Use `vtysh` if you use FRRouting containers as the lab devices.

## Using Output Filters

Unlike many other network operating systems, FRRouting `vtysh` does not have output filters. You probably don't need them as you'll be running FRR on top of a Unix-like operating system that supports pipes, but it might be a bit convoluted to use `vtysh` in a pipe.

To use the `vtysh` output in a pipe, you have to execute `vtysh` and get the results of a **show** command in a single command:

* You could use `sudo vtysh -c 'show command'` when you're in the **bash** shell of a lab device, for example:

```
r2(bash)#vtysh -c 'show isis database'|grep r2
r2.00-00             *     81   0x00000001  0xec86    1302    0/0/0
```

* Alternatively, you could use the `netlab connect --show` command to execute a `vtysh` **show** command on a lab device:

```
$ netlab connect r2 -q --show isis database|grep r2
r2.00-00             *     81   0x00000001  0xec86    1286    0/0/0
```

!!! tip
    Use `netlab connect --quiet --show` to omit the `Connecting to...` message.

The following table contains a mapping between common network operating system filters and Linux CLI commands:

| NOS filter | Linux CLI command |
|------------|-------------------|
| `include`  | `grep`            |
| `exclude`  | `grep -v`         |
| `begin`    | `grep -A 10000`[^SLN]   |
| `end`      | `grep -B 10000`   |
| `section`  | *no equivalent*   |

[^SLN]: The '10000' parameter specifies the number of lines after the match. Increase it for very long printouts ;)
