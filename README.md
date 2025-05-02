# ucore turnkey

## How to Use

Once you've booted into a [Fedora CoreOS live insallation environment](https://docs.fedoraproject.org/en-US/fedora-coreos/bare-metal/#_installing_from_live_iso), run the following command to interactively genrate an [ignition config](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/)

```sh
podman run -it -v ./:/data:z ghcr.io/ucore-turnkey
```
