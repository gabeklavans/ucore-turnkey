# ucore turnkey

## How to Use

Once you've booted into a [Fedora CoreOS live installation environment](https://docs.fedoraproject.org/en-US/fedora-coreos/bare-metal/#_installing_from_live_iso), run the following command to interactively generate an [ignition config](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/):

```sh
sh <(curl -L turn.dabe.tech)
```

> [!CAUTION]
> *Never* run scripts directly downloaded from the internet! Check the contents of the script first with `curl -L turn.dabe.tech` and you should see a relatively simple one-line command (along with a shebang).
