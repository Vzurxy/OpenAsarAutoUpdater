import requests
import re
from os import path, scandir
import psutil

NIGHTLY_RELEASE = "https://github.com/GooseMod/OpenAsar/releases/tag/nightly"
ASAR_DOWNLOAD = "https://github.com/GooseMod/OpenAsar/releases/download/nightly/app.asar"
TAG_REGEX = '<code class="f5\sml\-1">([a-z0-9]+)</code>'

session = requests.session()

def get_release_tag():
    nightly = session.get(NIGHTLY_RELEASE).content.decode("utf-8")
    match = re.search(TAG_REGEX, nightly)

    return match.group(1)


current_tag = None
latest_tag = get_release_tag()

with open("latest.txt", "r") as file:
    current_tag = file.read()


if current_tag == get_release_tag():
    print("You're already up to date!")
    exit()
else:
    print(f"""
        Not up to date.
        You have OpenAsar version: {"Not saved yet" if len(current_tag) == 0 else current_tag}.
        The latest version is: {latest_tag}.
    """)


app_data = path.expandvars(r'%LOCALAPPDATA%')
discord_apps = [ folder.name for folder in scandir(app_data) if folder.is_dir() and folder.name.find("Discord") != -1 ]

if len(discord_apps) == 0:
    print("Detected no installed Discord applications.")
    exit()
else:
    print(f"Detected {'multiple' if len(discord_apps) > 1 else 'a single'} Discord installation(s): {discord_apps}")

for name in discord_apps:
    discord_path = (f"{app_data}\{name}")
    app_path = None

    for folder in scandir(discord_path):
        if folder.name.find("app-") != -1:
            app_path = f"{discord_path}\{folder.name}"
            break

    print(f"Killing {name} processses...")

    for process in (process for process in psutil.process_iter() if process.name() == f"{name}.exe"):
        process.kill()

    asar_request = session.get(ASAR_DOWNLOAD)

    with open(f"{app_path}\\app.asar", "wb") as f:
        f.write(asar_request.content)

    print(f"Updated {name} using OpenAsar at {app_path}\\app.asar")
    print("Please reopen Discord!")


with open("latest.txt", "w") as f:
    f.write(latest_tag)
    pass


print(f"Updated latest tag to {latest_tag}.")
