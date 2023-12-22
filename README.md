# pymd3GUI
A GUI wrapper project for the Python project pymobiledevice3

## Introduction
...

## Detail description
...

## Cheatsheet

```bash
sudo mv /var/run/usbmuxd /var/run/usbmux_real
...
sudo socat -t100 -v UNIX-LISTEN:/var/run/usbmuxd,mode=777,reuseaddr,fork UNIX-CONNECT:/var/run/usbmux_real
...
sudo mv /var/run/usbmux_real /var/run/usbmux_real2
...
sudo socat -t100 -v UNIX-LISTEN:/var/run/usbmux_real,mode=777,reuseaddr,fork UNIX-CONNECT:/var/run/usbmux_real2
...
sudo mv /var/run/usbmux_real3 /var/run/usbmux_real2
```

## Author
- Kim David Hauser, DaVe inc. kim@kimhauser.ch, https://kimhauser.ch

## Credits
- https://github.com/doronz88/pymobiledevice3

- <a href="https://www.flaticon.com/free-icons/folder" title="folder icons">Folder icons created by kmg design - Flaticon</a>
- <a href="https://www.flaticon.com/free-icons/file" title="file icons">File icons created by Freepik - Flaticon</a>
- <div> Icons made by <a href="" title="Arkinasi"> Arkinasi </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
- <div> Icons made by <a href="https://www.flaticon.com/authors/uniconlabs" title="Uniconlabs"> Uniconlabs </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>