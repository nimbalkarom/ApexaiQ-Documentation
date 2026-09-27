# Linux advanced

---

## 1. What Is Linux?

| Point | Explanation |
|---|---|
| What it is | A free, open-source "kernel" — the core piece that many full operating systems are built around |
| Who made it | Linus Torvalds, back in 1991 |
| Where you'll see it | Servers, cloud systems, phones (Android runs on it), small embedded devices, and developer laptops |

---

## 2. Main Things That Make Linux, Linux

| Trait | What It Means |
|---|---|
| Open Source | Anyone can look at the code, change it, and share it |
| Multiuser | More than one person can use the same machine at the same time |
| Multitasking | It can run lots of programs at once without falling over |
| Portable | Works on almost anything — tiny gadgets all the way up to supercomputers |
| Secure | Has a solid permissions system, and far fewer viruses target it than Windows |
| Stable | Can stay running for a long time without needing a restart |
| Community-driven | Built and maintained by developers all over the world, not one company |

---

## 3. What Is GNU?

| Point | Explanation |
|---|---|
| What it is | A project started in 1983 to build a free, Unix-like operating system |
| What the name means | "GNU's Not Unix" — a joke acronym that refers to itself |
| What it gave us | All the tools you'd need to run an OS — compilers, editors, a shell — everything *except* a kernel |
| Why that matters | GNU had the tools but nothing to run them on. Linux showed up and filled that one missing piece — the kernel |

---

## 4. How the Linux Kernel Fits Together

Think of the kernel as a translator sitting between your software and your actual hardware.

| Layer | What It Does |
|---|---|
| Application | The programs you actually use — a browser, a text editor, whatever |
| Kernel | The core that controls hardware access, memory, running programs, and security. Sits right between your apps and your hardware |
| CPU | Does the actual work; the kernel decides which program gets CPU time and when |
| Memory | RAM; the kernel hands out and keeps track of memory for every program that's running |
| Devices | Hardware like your hard drive, network card, or keyboard — the kernel talks to them through drivers |

**In short:** an app asks the kernel for something → the kernel deals with the CPU, memory, and devices to make it happen.

---

## 5. GNU/Linux

| Point | Explanation |
|---|---|
| What it means | The full, technically correct name for what most people just call "Linux" |
| Why | "Linux" really only refers to the kernel. GNU is what supplied most of the tools that turn that kernel into a usable operating system |
| In everyday use | Almost everyone just says "Linux" for short, meaning the whole system, not just the kernel part |

---

## 6. What Is UNIX?

| Point | Explanation |
|---|---|
| What it is | An older operating system built in the 1970s at Bell Labs that shaped how Linux was designed |
| How it connects to Linux | Linux doesn't reuse UNIX's actual code, but it copies a lot of its ideas and structure — it's "UNIX-like" |
| Why it matters | A lot of familiar Linux ideas — files, permissions, the shell — trace straight back to UNIX |

---

## 7. What's a Linux Distribution?

| Point | Explanation |
|---|---|
| What it is | A ready-to-use package of Linux — the kernel plus a bundle of software, tools, and a way to install more software |
| Why there are so many | Different distributions are built for different jobs — servers, everyday desktops, security work, beginners just getting started, and so on |
| Common examples | Ubuntu, Debian, Fedora, CentOS, Red Hat, Arch Linux |

---

## 8. What Is a Shell?

| Point | Explanation |
|---|---|
| What it does | Takes the commands you type and turns them into something the operating system understands |
| Its job | It's the go-between connecting you and the kernel |
| Common types | Bash, Zsh, Fish, sh — Bash is the one most systems use by default |

---

## 9. How a Command Actually Runs: Terminal → Shell → OS

| Step | What Happens |
|---|---|
| Terminal | The window where you type. It's just the interface — it doesn't do anything with your commands itself |
| Shell | Reads what you typed, figures out what it means, and decides what needs to happen |
| OS (Kernel) | Actually does the work — opening files, running programs, talking to hardware |

**In short:** you type something in the Terminal → the Shell figures out what you meant → the Kernel carries it out.

---

## 10. What Is Bash?

| Point | Explanation |
|---|---|
| Full name | Bourne Again Shell |
| What it is | The most commonly used shell on Linux, and the default on most systems |
| Why people like it | It's powerful for writing scripts, well documented, and available pretty much everywhere |

---

## 11. Linux Commands — A Quick Overview of Categories

Commands generally fall into a handful of buckets:

| Category | What It Covers |
|---|---|
| Network | Checking your connection, IP details, downloading files |
| Shells | The different command interpreters out there (Bash, Zsh, etc.) |
| System Info | Checking hardware, memory, disk space, running processes |
| Command Info | Getting help or documentation for a command |
| Symbols | Special characters that change how a command behaves (see below) |
| Filters | Reshaping or processing text output |
| Hotkeys | Keyboard shortcuts you can use in the terminal |
| File System | Moving around and managing files and folders |
| Line Editors | Editing a file line by line (like `sed`) |
| File Editors | Full text editors you run in the terminal (like `nano` or `vim`) |

---

## 12. Special Symbols You'll Run Into

| Symbol | Name | What It Does | Example |
|---|---|---|---|
| `>` | Redirect (overwrite) | Sends a command's output into a file, wiping out whatever was there before | `echo "hello" > out.txt` → the file now just says `hello` |
| `>>` | Redirect (append) | Sends output into a file, but adds it to the end instead of erasing anything | `echo "world" >> out.txt` → the file now has `hello` then `world` |
| `<` | Redirect input | Feeds a file's contents into a command as its input | `sort < names.txt` |
| `\|` | Pipe | Takes one command's output and feeds it straight into the next command | `echo -e "banana\napple" \| sort` → prints `apple` then `banana` |
| `&&` | AND | Only runs the second command if the first one worked | `true && echo "ran"` → prints `ran` |
| `\|\|` | OR | Only runs the second command if the first one failed | `false \|\| echo "ran"` → prints `ran` |
| `;` | Command separator | Runs several commands one after another, no matter what happens with each | `echo one; echo two` → prints both |
| `&` | Background | Runs a command in the background so you get your terminal back right away | `sleep 5 &` |
| `*` | Wildcard (multiple characters) | Stands in for any number of characters in a filename | `ls *.txt` → matches every `.txt` file |
| `?` | Wildcard (single character) | Stands in for exactly one character | `ls file?.txt` matches `file1.txt` but not `file10.txt` |
| `~` | Home directory | Shortcut for your own home folder | `echo ~` → `/root` (or `/home/yourname`) |
| `$` | Variable reference | Pulls out the value stored in a variable | `NAME="test"; echo $NAME` → prints `test` |
| `#` | Comment | Everything after it on that line gets ignored in a script; also shows up as the root user's prompt symbol | `# this is a comment` |
| `!` | History / negation | Brings back previous commands (`!!` reruns the last one), or flips a condition |
