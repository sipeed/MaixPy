import os
import sys
import requests
import subprocess

curr_dir = os.path.abspath(os.path.dirname(__file__))

def get_release_image_url(tag_name):
    owner = "sipeed"
    repo = "LicheeRV-Nano-Build"
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"

    # Make the request to the GitHub API
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        releases = response.json()
        # Print the release information
        for release in releases:
            if release['tag_name'] == tag_name:
                for asset in release['assets']:
                    if asset['name'].endswith(".img.xz"):
                        return asset['browser_download_url'], asset['name']
    else:
        raise Exception(f"Failed to retrieve releases: {response.status_code}")
    return None, None

def download_file(url, output_path, force=False):
    save_dir = os.path.dirname(output_path)
    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if os.path.exists(output_path) and not force:
        print(f"-- file {os.path.basename(output_path)} already exists, skip download")
        return
    try:
        # Use subprocess to call wget
        subprocess.run(
            ["wget", "--progress=dot:giga", "-O", output_path, url],
            check=True
        )
        print(f"Download completed: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def get_base_image(file_path = ""):
    version_txt = os.path.join(curr_dir, "..", "..", "maix", "version_base_system.txt")
    with open(version_txt, "r") as f:
        version = f.readline().strip()
    url, filename = get_release_image_url(version)
    if not url:
        raise Exception("get base system image download url failed")
    print(f"-- download base system {filename} from url: {url}")
    if not file_path:
        file_path = os.path.join(curr_dir, "tmp", filename)
    download_file(url, file_path)
    return file_path


if __name__ == "__main__":
    import argparse
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument(
        "-o", "--out", help="download file path, default will save to tmp/***.img.xz", default=""
    )
    args = args_parser.parse_args()

    base_system_path = get_base_image(args.out)
    print(f"\n-- got base system: {base_system_path}")

