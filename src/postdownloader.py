"""Scan and download posts from a list of URLs."""

import sys
import time
import os
import requests
from utilfilepath import filepath


def download_posts(offline_test_mode=False):
    """Scan and download all URLs in Posts."""
    num_posts = 0
    num_skipped_posts = 0
    total_file_size = 0

    headers = {"User-Agent": "FuzzySearch v1.0.0 (by alsarynnn on e621)"}

    # Keep track of file type statistics
    static_types = [".jpg", ".png", ".jpeg", ".jfif", ".bmp", ".JPG", ".webp"]
    video_types = [".mkv", ".mp4", ".webm"]
    num_static = 0
    num_gif = 0
    num_flash = 0
    num_video = 0
    num_other = 0

    # Check each input file is properly-formatted before downloading any posts.
    print("Checking Posts/ for posts")
    num_files = 0
    for filename in os.listdir(filepath.downloads_dir):
        file_path = filepath.downloads_dir / filename
        # Ignore directories
        if os.path.isfile(file_path):
            print(f"  Scanning file {filename}")
            num_files += 1
            with open(file_path, "rt", encoding="utf-8") as in_file:
                # Make a folder with the same name as the input file
                # (minus file extension)
                dir_name = filepath.downloads_dir / filename[0:filename.find(".")]
                dir_name.mkdir(parents=True, exist_ok=True)
                # Scan each row of the input file.
                for line in in_file:
                    line = line.strip("\n").split("\t")
                    # If the line doesn't have 3 elements,
                    # then we've reached the end of the file.
                    if len(line) != 3:
                        break

                    # Each line has the format: post_name.type url file_size
                    post_filename = dir_name / line[0]
                    # Skip over already downloaded posts.
                    if post_filename.exists():
                        num_skipped_posts += 1
                    # Else, plan to download the post
                    else:
                        num_posts += 1
                        total_file_size += float(line[2])

                        # Investigate file type
                        filetype = f".{line[0].partition('.')[2]}"
                        if filetype in static_types:
                            num_static += 1
                        elif filetype == ".gif":
                            num_gif += 1
                        elif filetype == ".swf":
                            num_flash += 1
                        elif filetype in video_types:
                            num_video += 1
                        else:
                            num_other += 1
                            print(f"Unknown filetype found: {post_filename}")

    # Print an estimated time to download all posts, alongside other stats.
    download_speed_mbs = 4
    estimated_time = round((total_file_size / download_speed_mbs) / 60, 2)
    print(f"Skipped {num_skipped_posts} posts that already were downloaded.")
    print(f"Found {num_posts} posts totalling {round(total_file_size, 2)} MB")
    print(f"Estimated running time of {estimated_time} min.\n")

    time.sleep(3)

    # num_spaces: used to pretty-print progress reports
    num_spaces = len(str(num_posts))
    program_start_time = time.time()
    curr_post = 0
    curr_file = 0
    for filename in os.listdir(filepath.downloads_dir):
        file_path = filepath.downloads_dir / filename
        # Ignore directories
        if os.path.isfile(file_path):
            with open(file_path, "rt", encoding="utf-8") as in_file:
                dir_name = filepath.downloads_dir / filename[0:filename.find(".")]
                curr_file += 1
                print(f"{curr_file}/{num_files}: {dir_name.stem}")
                # Scan each row of the file.
                for line in in_file:
                    line = line.strip("\n").split("\t")
                    # If the line doesn't have 3 elements,
                    # then we've reached the end of the file.
                    if len(line) != 3:
                        break
                    # Each line has the format: post_name.type url file_size
                    size = round(float(line[2]), 2)
                    filename = dir_name / line[0]
                    # Skip over already downloaded posts.
                    if filename.exists():
                        num_skipped_posts += 1
                    # Else, attempt to download the post
                    else:
                        curr_post += 1
                        print(
                            f"[{str(curr_post).rjust(num_spaces)}/{num_posts}:"
                            f" {dir_name.stem}/{line[0]}] ({size} MB):",
                            end="",
                        )
                        start_time = time.time()
                        if offline_test_mode:
                            status_code = 200
                        else:
                            status_code = get_post(filename, headers, line[1])
                        if status_code != 200:
                            print(
                                " Invalid status code "
                                + str(status_code)
                                + " Exiting..."
                            )
                            sys.exit(1)
                        duration = round(time.time() - start_time, 2)
                        if duration == 0:
                            download_rate = 0
                        else:
                            download_rate = round(size / duration, 2)
                        print(f" Finished! {duration}s ({download_rate} MB/s)")

    # Print stats
    total_running_time = time.time() - program_start_time
    print(f"Downloaded {num_posts} posts totalling {round(total_file_size, 2)} MB")
    print(f"Running time: {round(total_running_time, 2)}s")
    print(
        f"Average download speed: "
        f"{round(total_file_size / total_running_time, 2)} MB/s\n"
    )


def get_post(out_filename, headers, url: str):
    """Make a single request to url and stores file."""
    with open(out_filename, "wb") as out_file:
        try:
            response = requests.get(url, headers=headers, timeout=20)
            out_file.write(response.content)
        except requests.exceptions.Timeout:
            print("The request timed out.")
            return 799
    return response.status_code
