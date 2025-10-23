---
title: Installation and Setup
---
# Software Installation and Lab Setup

It's easiest to use the IS-IS labs with _[netlab](https://netlab.tools/)_. Still, you can use most of them (potentially with slightly reduced functionality) with any other virtual lab environment or on physical gear. For the rest of this document, we'll assume you decided to use _netlab_; if you want to set up your lab in some other way, read the [Manual Setup](https://bgplabs.net/external/) section of the BGP Labs documentation.

!!! Warning
    IS-IS labs work best with _netlab_ release 2.0.0 or later (some lab exercises require a more recent _netlab_ release). If you're using an earlier release, please upgrade with `pip3 install --upgrade networklab`.

## Select the Network Devices You Will Work With

You can run FRRouting in all [_netlab_-supported virtualization environments](https://netlab.tools/providers/) (libvirt virtual machines or Docker containers)[^CSF], and if you want to start practicing IS-IS with minimum hassle, consider using FRRouting for all lab devices[^ML]. You can even run Arista cEOS, FRRouting, or Nokia SR Linux containers on [MacBooks with Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html).

[^CSF]: There is no official FRR virtual machine image -- _netlab_ has to download and install FRR on a Ubuntu VM whenever you start an `frr` node as a virtual machine. Using FRR containers is faster and consumes way less bandwidth or memory.

[^ML]: Unless you want to work on multi-level IS-IS configuration, in which case FRRouting is useless. It cannot distribute level-1 IS-IS routes into level-2 topology or vice versa.

If you'd like to use a more traditional networking device, use any other [_netlab_-supported device](https://netlab.tools/platforms/) for which we implemented [basic IS-IS configuration](https://netlab.tools/module/isis/#platform-support) as the device to practice with[^x86]. I recommend Arista cEOS or Nokia SR Linux containers; they are the easiest ones to install and use.

!!! tip
    If you plan to run the labs in [free GitHub Codespaces](4-codespaces.md), you MUST use container-based network devices like Arista cEOS, FRR, Nokia SR Linux, or Vyos.

[^x86]: Most network devices require an x86 CPU. You must run the labs on a device with an x86 CPU (Intel or AMD) to use them.

## Select the Additional Devices in Your Lab

Some labs use additional routers -- preconfigured devices with which your routers exchange routing information. You won't configure those devices, but you might have to log into them and execute **show** commands.

The default setup uses FRRouting for additional routers; we also generated all the **show** printouts with FRRouting. Alternatively, you can use any other device for which we [implemented basic IS-IS configuration](https://netlab.tools/module/isis/#platform-support) as additional routers. Additional limitations (should they exist) are listed under the *Device Requirements* section of individual lab exercises.

## Select the Virtualization Environment

Now that you know which network device to use, check [which virtualization environment](https://netlab.tools/platforms/#supported-virtualization-providers) you can use. Running IS-IS labs in a [free GitHub Codespace](4-codespaces.md) is an excellent starting point, but if you decide to build your own infrastructure, _containerlab_ is easier to set up than _libvirt_.

If you want to run the labs on your laptop (including [Macs with Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon/)), create a [Ubuntu VM](https://netlab.tools/install/ubuntu-vm/) to run _netlab_. You could also run them in a VM in a private or public cloud or invest in a tiny brick of densely packed silicon ([example](https://www.minisforum.com/)).

Now for a few gotchas:

* Your hardware and virtualization software (for example, VirtualBox or VMware Fusion) must support _nested virtualization_ if you want to run virtual machines on that Ubuntu VM.
* You don't need nested virtualization to run Docker containers unless you're using containers that run virtual machines _within a container_ (the [*vrnetlab* approach](https://netlab.tools/labs/clab/#using-vrnetlab-containers)).

## Software Installation

Based on the choices you made, you'll find the installation instructions in one of these documents:

* [Using GitHub Codespaces](4-codespaces.md)
* [Ubuntu VM Installation](https://netlab.tools/install/ubuntu-vm/) on Windows or MacOS
* [Ubuntu Server Installation](https://netlab.tools/install/ubuntu/)
* [Running netlab on any other Linux Server](https://netlab.tools/install/linux/)
* [Running netlab in a Public Cloud](https://netlab.tools/install/cloud/)
* [Running netlab on Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html)

Once you have completed the software installation, you have to deal with the stupidities of downloading and installing network device images ([libvirt](https://netlab.tools/labs/libvirt/#vagrant-boxes), [containers](https://netlab.tools/labs/clab/#container-images)) unless you decided to use FRR, Nokia SR Linux, or Vyos.

I would love to simplify the process, but the networking vendors refuse to play along. Even worse, their licenses prohibit me from downloading the images and creating a packaged VM with preinstalled network devices for you[^NPAL]. Fortunately, you only have to go through this colossal waste of time once.

[^NPAL]: I'm not going to pay a lawyer to read their boilerplate stuff, and I'm definitely not going to rely on my amateur understanding of US copyright law.

## Setting Up the Labs {#defaults}

We finally got to the fun part -- setting up the labs. If you're not using GitHub Codespaces:

* Select a directory where you want to have the IS-IS labs
* Clone the `isis` [GitHub repository](https://github.com/bgplab/isis) with `git clone https://github.com/bgplab/isis.git`. [GitHub UI](https://github.com/bgplab/isis) gives you other options in the green `Code` button, including _Download ZIP_

After you get a local copy of the repository:

* Change the directory to the top directory of the cloned repository[^BLB].
* Verify the current project defaults with the `netlab defaults --project` command:

```
$ netlab defaults --project
device = frr (project)
groups.external.device = frr (project)
paths.plugin = ['topology:.', 'topology:../../plugin', 'package:extra'] (project)
provider = clab (project)
```

[^BLB]: `isis` if you used the simple version of the **git clone** command

* If needed, change the project defaults to match your environment with the `netlab defaults --project _setting_=_value_` command or edit the `defaults.yml` file with a text editor like `vi` or `nano`. For example, use these commands to change your devices to Cisco CSRs running as virtual machines[^CSR]:

```shell
$ netlab defaults --project device=csr
The default setting device is already set in project defaults
Do you want to change that setting in project defaults [y/n]: y
device set to csr in /home/user/isis/defaults.yml

$ netlab defaults --project provider=libvirt
The default setting provider is already set in netlab,project defaults
Do you want to change that setting in project defaults [y/n]: y
provider set to libvirt in /home/user/isis/defaults.yml
```

[^CSR]: Assuming you built the [CSR Vagrant box](https://netlab.tools/labs/csr/) first

* In a terminal window, change the current directory to one of the lab directories (for example, `basic/1-simple-ipv4`), and execute **netlab up**.
* Wait for the lab to start and use **netlab connect** to connect to individual lab devices
* Have fun.
* When you're done, collect the device configurations with **netlab collect** (if you want to save them) and shut down the lab with **netlab down**
* Change the current directory to another lab directory and repeat.
* Once you run out of lab exercises, create a new one and contribute it with a pull request ;)
