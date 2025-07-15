import os, subprocess, datetime

def git_autobackup():
    from streamlit.runtime.secrets import secrets

    os.environ["GIT_AUTHOR_NAME"] = secrets["GIT_USER"]
    os.environ["GIT_COMMITTER_NAME"] = secrets["GIT_USER"]
    os.environ["GIT_AUTHOR_EMAIL"] = secrets["GIT_EMAIL"]
    os.environ["GIT_COMMITTER_EMAIL"] = secrets["GIT_EMAIL"]

    repo_url = f"https://{secrets['GIT_USER']}:{secrets['GIT_TOKEN']}@{secrets['REPO_URL']}"
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    commands = [
        f'git config user.name "{secrets["GIT_USER"]}"',
        f'git config user.email "{secrets["GIT_EMAIL"]}"',
        "git add glass_defects.db",
        f'git commit -m "🔁 Auto-backup at {now}"',
        f"git push {repo_url} HEAD:main"
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error in: {cmd}\n{e.stderr}")
