py-sth
======

Python storage tank helper.  Basically a program that syncs filesystems/folder to elasticsearch and reports health status for devices, raid and other sysops related things. Developed to work on both FreeBSD and Linux. It is not using kqueue to handle filesystem events as it use filedescriptiors for watching changes. That solution can't scale so syncing is therefore polled.

MIT Licensed
