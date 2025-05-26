import subprocess
from typing import cast

import questionary
import requests
import yaml
from github import Github, UnknownObjectException
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser
from yaml import load


def get_gh_named_user(
    gh: Github,
    username: str,
) -> tuple[bool, NamedUser | AuthenticatedUser | None]:
    gh_user = None
    try:
        gh_user = gh.get_user(username)
    except UnknownObjectException:
        return (False, gh_user)

    return (True, gh_user)


def update_butane(
    butane_yaml, username: str, password_hash: str, version: str, pubkeys: list[str]
):
    """
    replace values in the butane content with user-supplied ones
    """

    butane_yaml["passwd"]["users"][0]["name"] = username
    butane_yaml["passwd"]["users"][0]["groups"] = ["wheel"]
    butane_yaml["passwd"]["users"][0]["password_hash"] = password_hash
    if len(pubkeys) > 0:
        butane_yaml["passwd"]["users"][0]["ssh_authorized_keys"] = pubkeys
    else:
        del butane_yaml["passwd"]["users"][0]["ssh_authorized_keys"]

    butane_yaml["systemd"]["units"][0]["contents"] = butane_yaml["systemd"]["units"][0][
        "contents"
    ].replace("ghcr.io/ublue-os/ucore", f"ghcr.io/ublue-os/{version}")
    butane_yaml["systemd"]["units"][1]["contents"] = butane_yaml["systemd"]["units"][1][
        "contents"
    ].replace("ghcr.io/ublue-os/ucore", f"ghcr.io/ublue-os/{version}")


def str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    """
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


def main():
    username = questionary.text("Enter your desired account username").ask()
    password = questionary.password("Enter your desired account password").ask()
    password_hash = ""
    try:
        password_hash = (
            subprocess.check_output(["mkpasswd", "--method=yescrypt", password])
            .decode("utf-8")
            .strip("\n")
        )
    except Exception as exc:
        raise Exception("Error during password hash generation.") from exc

    version = questionary.select(
        "Select a version of ucore",
        choices=["ucore", "ucore-minimal", "ucore-hci", "fedora-coreos"],
    ).ask()

    # I'm pretty sure just instantiating the Github object doesn't make any HTTP request; might need to confirm that, though.
    # I want to avoid making any unnecessary requests.
    gh = Github()
    pubkeys = []
    while True:
        gh_username = questionary.text(
            "Enter your GitHub username (leave blank to skip)",
            instruction="This is only used to get SSH public keys associated with the GitHub account. These will be added to the account created for this machine for easy login access.",
            default="",
        ).ask()

        if gh_username == "":
            break

        gh_user_found, gh_user = get_gh_named_user(gh, gh_username)
        if not gh_user_found:
            questionary.print(
                f'The GitHub user "{gh_username}" was not found. Please enter a valid username or enter a blank value to skip this step.',
                style="fg:red",
            )
            continue

        gh_user = cast(NamedUser, gh_user)
        pubkeys = [pubkey.key for pubkey in gh_user.get_keys()]
        break

    # get the autorebase butane file provided by ucore and fill in the user's inputs
    yaml.add_representer(str, str_presenter)
    res = requests.get(
        "https://raw.githubusercontent.com/ublue-os/ucore/refs/heads/main/examples/ucore-autorebase.butane",
        timeout=10,
    )
    res_content = res.content.decode("utf-8")
    butane_yaml = yaml.safe_load(res_content)

    update_butane(butane_yaml, username, password_hash, version, pubkeys)

    butane_file_path = "/data/ucore-autorebase-custom.butane"
    with open(butane_file_path, "w", encoding="utf-8") as butane_file:
        butane_file.write(yaml.dump(butane_yaml))

    ignition_file_path = "/data/config.ign"
    try:
        with open(ignition_file_path, "w", encoding="utf-8") as ignition_file:
            subprocess.run(
                [
                    "butane",
                    "--pretty",
                    "--strict",
                    butane_file_path,
                ],
                check=True,
                stdout=ignition_file,
            )
    except Exception as exc:
        raise Exception("Error during butane transpilation.") from exc

    questionary.print(
        "You should now have an ignition config in your file system if you created the proper volume mount according to the ucore-turnkey README. To continue the ucore installtion with your config, run the following command:\n",
        style="fg:green",
    )
    questionary.print(
        f"sudo coreos-installer install -i .{ignition_file_path} /dev/<your-storage-device>\n",
    )
    questionary.print(
        "If you're unsure of your storage device name, try running lsblk to find it.",
        style="fg:yellow",
    )


if __name__ == "__main__":
    main()
