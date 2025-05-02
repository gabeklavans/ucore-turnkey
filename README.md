# ucore turnkey

## How to Use

Once you've booted into a [Fedora CoreOS live installation environment](https://docs.fedoraproject.org/en-US/fedora-coreos/bare-metal/#_installing_from_live_iso), run the following command to interactively generate an [ignition config](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/)

```sh
mkdir data && podman run -it -v ./data:/data:z ghcr.io/gabeklavans/ucore-turnkey
```
