---
title: Installation and Setup
---
# Software Installation and Lab Setup

It's easiest to use the IS-IS labs with _[netlab](https://netlab.tools/)_. Still, you can use most of them (potentially with slightly reduced functionality) with any other virtual lab environment or on physical gear. For the rest of this document, we'll assume you decided to use _netlab_; if you want to set up your lab in some other way, read the [Manual Setup](https://bgplabs.net/external/) section of the BGP Labs documentation.

!!! Warning
    IS-IS labs work best with _netlab_ release 1.8.3 or later. If you're using an earlier _netlab_ release, please upgrade with `pip3 install --upgrade networklab`.

## Select the Network Devices You Will Work With

You can run FRRouting in all [_netlab_-supported virtualization environments](https://netlab.tools/providers/) (VirtualBox, libvirt, or Docker)[^CSF], and if you want to start practicing IS-IS with minimum hassle, consider using it for all lab devices. You can even [run FRRouting containers on Macbooks with Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html).

If you'd like to use a more traditional networking device, use any other [_netlab_-supported device](https://netlab.tools/platforms/) for which we implemented [basic IS-IS configuration](https://netlab.tools/module/isis/#platform-support) as the device to practice with[^x86]. I recommend Arista cEOS or Nokia SR Linux containers; they are the easiest ones to install and use.

!!! tip
    If you plan to run the labs in [free GitHub Codespaces](4-codespaces.md), you MUST use container-based network devices like Arista cEOS, FRR, Nokia SR Linux, or Vyos.

[^x86]: In that case, you will have to run the labs on a device with an x86 CPU (Intel or AMD).

## Select the Additional Devices in Your Lab

Some labs use additional routers -- preconfigured devices with which your routers exchange routing information. You won't configure those devices, but you might have to log into them and execute **show** commands.

The default setup uses FRRouting for additional routers; you can use any other device for which we [implemented basic IS-IS configuration](https://netlab.tools/module/isis/#platform-support). Additional limitations (should they exist) are listed under the *Device Requirements* section of individual lab exercises.

[^CSF]: There is no official FRR virtual machine image -- _netlab_ has to download and install FRR on a Ubuntu VM whenever you start an `frr` node as a virtual machine. Using FRR containers is faster and consumes way less bandwidth or memory.

## Select the Virtualization Environment

Now that you know which network device to use, check [which virtualization environment](https://netlab.tools/platforms/#supported-virtualization-providers) you can use. I would prefer _containerlab_ over _libvirt_ with _virtualbox_ being a distant third, but that's just me.

!!! tip
    You can also run the IS-IS labs in a [free GitHub Codespace](4-codespaces.md).

A gotcha: You can use _virtualbox_ if you want to run the lab devices as virtual machines on your Windows- or MacOS laptop with Intel CPU, but even then, I'd prefer running them in a [Ubuntu VM](https://netlab.tools/install/ubuntu-vm/).

One more gotcha: your hardware and virtualization software (for example, VirtualBox or VMware Fusion) must support _nested virtualization_ if you want to use _libvirt_ on that Ubuntu VM. You don't need nested virtualization to run Docker containers unless you're using the crazy trick we're forced to use for Juniper vMX or Nokia SR OS -- they're running as a virtual machine _within a container_.

## Software Installation

Based on the choices you made, you'll find the installation instructions in one of these documents:

* [Using GitHub Codespaces](4-codespaces.md)
* [Ubuntu VM Installation](https://netlab.tools/install/ubuntu-vm/) on Windows or MacOS
* [Ubuntu Server Installation](https://netlab.tools/install/ubuntu/)
* [Running netlab on any other Linux Server](https://netlab.tools/install/linux/)
* [Running netlab in a Public Cloud](https://netlab.tools/install/cloud/)
* [Running netlab on Apple silicon](https://blog.ipspace.net/2024/03/netlab-bgp-apple-silicon.html)
* Discouraged: [Virtualbox-Based Lab on Windows or MacOS](https://netlab.tools/labs/virtualbox/)

Once you have completed the software installation you have to deal with the stupidities of downloading and installing network device images ([Virtualbox](https://netlab.tools/labs/virtualbox/), [libvirt](https://netlab.tools/labs/libvirt/#vagrant-boxes), [containers](https://netlab.tools/labs/clab/#container-images)) unless you decided to use FRR, Nokia SR Linux, or Vyos.

I would love to simplify the process, but the networking vendors refuse to play along. Even worse, their licenses prohibit me from downloading the images and creating a packaged VM with preinstalled network devices for you[^NPAL]. Fortunately, you only have to go through this colossal waste of time once.

[^NPAL]: I'm not going to pay a lawyer to read their boilerplate stuff, and I'm definitely not going to rely on my amateur understanding of US copyright law.

## Setting Up the Labs {#defaults}

We finally got to the fun part -- setting up the labs. If you're not using GitHub Codespaces:

* Select a directory where you want to have the IS-IS labs
* Clone the `isis` [GitHub repository](https://github.com/bgplab/isis) with `git clone https://github.com/bgplab/isis.git`. [GitHub UI](https://github.com/bgplab/isis) gives you other options in the green `Code` button, including _Download ZIP_

After you get a local copy of the repository:

* If needed, edit the `defaults.yml` file in the top directory to set your preferred network device and virtualization environment. For example, I'm using the following settings to run the labs with Arista EOS containers while using FRR as the external BGP feeds:

```
device: eos             # Change to your preferred network device
provider: clab          # Change to virtualbox or libvirt if needed

groups:
  external:
    device: frr         # Change to your preferred external router
```

* In a terminal window, change the current directory to one of the lab directories (for example, `basic/1-session`), and execute **netlab up**.
* Wait for the lab to start and use **netlab connect** to connect to individual lab devices
* Have fun.
* When you're done, collect the device configurations with **netlab collect** (if you want to save them) and shut down the lab with **netlab down**
* Change the current directory to another lab directory and repeat.
* Once you run out of lab exercises, create a new one and contribute it with a pull request ;)
