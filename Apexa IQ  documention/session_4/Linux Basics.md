 Linux Basics

---

## 1. What Is Linux?

| Point | Explanation |
|---|---|
| What it is | A free, open-source operating system that plays the same role Windows or macOS does |
| Where you'll find it | Running servers, powering cloud infrastructure, sitting on developer machines, and quietly running most of the internet's backend |
| How we'll be using it | Mostly through the **terminal** — typing out commands instead of clicking around a GUI |
| Distributions | Linux comes in different "flavors" (Ubuntu, CentOS, Debian, Fedora) — same core underneath, just packaged differently |

---

## 2. How the File System Is Laid Out

| Folder | What Lives There |
|---|---|
| `/` | Root — the very top of the file system; everything else sits inside it |
| `/home` | Each user gets their own personal folder here |
| `/etc` | System-wide configuration files |
| `/bin` | The essential command-line programs the system relies on |
| `/var` | Files that change frequently, like logs |
| `/tmp` | Temporary files that get cleared out periodically |
| `/root` | The administrator (root) account's personal folder |

---

## 3. Getting Around: Navigation Commands

| Command | What It Does |
|---|---|
| `pwd` | Tells you which folder you're currently in |
| `ls` | Lists what's in the current folder |
| `ls -l` | Same thing, but with extra detail — permissions, size, date |
| `ls -a` | Lists everything, including hidden files |
| `cd foldername` | Moves you into a folder |
| `cd ..` | Steps up one folder |
| `cd ~` | Jumps straight back to your home folder |

---

## 4. Working with Files and Folders

| Command | What It Does |
|---|---|
| `touch file.txt` | Creates a new, empty file |
| `mkdir foldername` | Creates a new folder |
| `cp source destination` | Copies a file |
| `mv source destination` | Moves or renames a file |
| `rm file.txt` | Deletes a file |
| `rm -r foldername` | Deletes a folder and everything inside it |

---

## 5. Looking Inside Files

| Command | What It Does |
|---|---|
| `cat file.txt` | Dumps the whole file to the screen at once |
| `less file.txt` | Lets you scroll through the file one screen at a time |
| `head file.txt` | Shows just the first few lines |
| `tail file.txt` | Shows just the last few lines |
| `nano file.txt` | Opens a simple built-in editor so you can edit the file directly |

---

## 6. File Permissions, in Brief

| Point | Explanation |
|---|---|
| Who | Every file has an Owner, a Group, and everyone else (Others) |
| What | Each of those can be given Read (r), Write (w), and Execute (x) permission |
| Checking | Run `ls -l` and look at the string at the start of each line, something like `-rwxr-xr--` |
| Changing | `chmod` adjusts permissions; `chown` changes who owns the file |

---

## 7. Checking In on the System

| Command | What It Does |
|---|---|
| `whoami` | Tells you which user you're currently logged in as |
| `date` | Shows the current date and time |
| `df -h` | Shows how much disk space is being used |
| `top` | Shows what processes are currently running and how much they're using |
| `history` | Shows the commands you've recently run |

---

## 8. Installing Software: Package Management Basics

| Point | Explanation |
|---|---|
| What it is | The system Linux uses to install, update, or remove software |
| On Ubuntu/Debian | `apt` is the go-to tool — e.g. `sudo apt install packagename` |
| On CentOS/Fedora | `yum` or `dnf` does the same job |
| `sudo` | Runs a command with administrator privileges — you'll need it for installs and most system-level changes |

---

## 9. A Handful of Other Things Worth Knowing

| Term | Meaning |
|---|---|
| Terminal | The window where you actually type your commands |
| Shell | The program running behind the scenes that reads and executes those commands (Bash, for example) |
| Root user | The administrator account — full access to everything on the system |
| Case-sensitive | Linux treats `File.txt` and `file.txt` as two completely different files |
