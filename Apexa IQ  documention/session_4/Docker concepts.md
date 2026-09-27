# Docker — Complete Notes

---

## 1. What Are Containers?

| Point | Explanation |
|---|---|
| Old approach | Virtual Machines (VMs) — each app runs inside its own guest OS, on virtualized hardware |
| Problem with VMs | Full isolation, but heavy — a lot of computing power goes into virtualizing hardware |
| Container approach | Uses the host OS's own low-level mechanics — gives most of the isolation of a VM for a fraction of the resource cost |
| In short | Docker is a container-based system that lets an app run in its own lightweight, isolated space |

### VMs vs Containers

| VMs | Containers |
|---|---|
| Heavyweight | Lightweight |
| Limited performance | Near-native performance |
| Each VM runs its own OS | All containers share the host OS |
| Hardware-level virtualization | OS-level virtualization |
| Starts in minutes | Starts in milliseconds |
| Needs a fixed chunk of memory | Uses less memory |
| Fully isolated, generally more secure | Process-level isolation, slightly less secure |

---

## 2. Types of Containers

| Type | Notes |
|---|---|
| LXC (Linux Containers) | The original container technology; OS-level virtualization for running several isolated Linux systems on one host |
| Docker | Started as a way to build single-app LXC containers, then grew into its own full container runtime |
| Other providers | LXD, CGManager, Singularity, Windows Server Containers |

---

## 3. What Is Docker?

| Point | Explanation |
|---|---|
| Simple definition | A tool that lets developers package an app with everything it needs into a standard, portable unit (a container) |
| Key benefit | Bundles the app + all its dependencies together, so it runs the same everywhere |
| vs VMs | Much lower overhead, so resources get used more efficiently |

### When to Use Docker

- Trying out new tools without a messy install/setup
- Simple, standard apps that fit an existing image on Docker Hub (e.g. a LAMP site)
- Keeping multiple apps on one server isolated from each other
- Giving a dev team identical local environments that match production

### When Not to Use Docker

- The app is complex and there's no dedicated sysadmin to manage it
- Performance is absolutely critical (containers are fast, but not quite native speed)
- Security is the top priority and no security engineer is available to handle container-specific risks
- You need to run/test the same app across different operating systems
- You need a full cluster manager (Docker alone isn't a replacement for tools like Ansible or Kubernetes)

---

## 4. Container Architecture

| Component | Role |
|---|---|
| **Client** | Where you run `docker` commands — locally or via a remote API (build, pull, run) |
| **Runtime (Daemon)** | Manages containers and images; carries out what the client asks for |
| **Registry** | Stores images remotely, so they can be pulled and shared |

---

## 5. Core Components of Docker Engine

| Component | Role |
|---|---|
| **Server (dockerd)** | The background process (daemon) that creates and manages images, containers, networks, and volumes |
| **REST API** | Defines how applications talk to the server and tell it what to do |
| **Client** | The command-line interface (`docker`) you actually type commands into |

---

## 6. Key Terminology

| Term | Meaning |
|---|---|
| Docker Image | A template containing the app and everything it needs to run |
| Docker Container | A running instance of an image |
| Docker Hub | The official public registry where Docker images are stored and shared |
| Dockerfile | A text file with instructions for building an image |

---

## 7. Docker Editions

| Edition | Best For |
|---|---|
| Community Edition (CE) | Individual developers and small teams; fewer features |
| Enterprise Edition (EE) | Large teams and production use; split into Basic, Standard, and Advanced tiers |

---

## 8. Installing Docker (Ubuntu 20.04)

### Using APT

| Step | Command |
|---|---|
| Update packages | `sudo apt update` |
| Install prerequisites | `sudo apt install curl apt-transport-https ca-certificates software-properties-common` |
| Add Docker's GPG key | `curl -fsSL https://download.docker.com/linux/ubuntu/gpg \| sudo apt-key add -` |
| Add Docker repo | `sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"` |
| Refresh package list | `sudo apt update` |
| Confirm using Docker's repo | `apt-cache policy docker-ce` |
| Install Docker | `sudo apt install docker-ce` |
| Start Docker | `sudo service docker start` |
| Check status | `sudo systemctl status docker` |
| Enable on boot | `sudo systemctl enable docker` |
| Check version | `docker --version` |
| Run without `sudo` (optional) | `sudo usermod -aG docker ubuntu` |

### Using Snap

| Step | Command |
|---|---|
| See available versions | `snap info docker` |
| Install | `sudo snap install docker` |
| Verify install | `snap services docker` |
| Start | `sudo snap start docker` |
| Stop | `sudo snap stop docker` |
| Remove | `sudo snap remove docker` |

---

## 9. Basic Container Commands

| Command | What It Does |
|---|---|
| `docker info` | Shows info about the Docker setup on your machine |
| `docker run -it ubuntu /bin/bash` | Runs a container and drops you into an interactive shell |
| `docker run -h NAME -it ubuntu /bin/bash` | Same, but names the container |
| `docker run --name mywildfly -d -p 8080:8080 jboss/wildfly` | Runs a container in the background (detached), mapping a port |
| `docker ps` | Lists currently running containers |
| `docker ps -a` | Lists all containers, running or not |
| `docker inspect CONTAINER_NAME` | Shows detailed info about a container |
| `docker start CONTAINER_NAME` | Starts a stopped container |
| `docker attach CONTAINER_NAME` | Enters the shell of a running container |
| `docker exec -it CONTAINER_NAME bash` | Runs a new command (e.g. bash) inside a running container |
| `docker logs -f CONTAINER_NAME` | Follows a container's logs in real time |
| `docker stop CONTAINER_NAME` | Stops a container |
| `docker pause` / `docker unpause` | Pauses/resumes all processes inside a container |
| `docker rm CONTAINER_NAME` | Deletes a container |
| `docker rm -f CONTAINER_NAME` | Force-stops and deletes a container |
| `docker rename OLD NEW` | Renames a container |
| `docker rm $(docker ps -aq)` | Removes all containers at once |

---

## 10. Docker Images

| Command | What It Does |
|---|---|
| `docker images` | Lists images stored locally |
| `docker pull ubuntu` | Downloads an image from a registry |
| `docker run ubuntu:20.04 ...` | Runs a specific version (tag) of an image |
| `docker build -t myimage:tag <path>` | Builds an image from a Dockerfile |
| `docker history <image>` | Shows how an image was built, layer by layer |
| `docker tag <image> <new-name>:<tag>` | Gives an image a new name/tag |
| `docker rmi <image>` | Deletes a local image |
| `docker save -o file.tar <image>` | Exports an image to a `.tar` file |
| `docker load -i file.tar` | Imports an image from a `.tar` file |

---

## 11. Docker Registry

| Command | What It Does |
|---|---|
| `docker login` | Logs in to a registry (Docker Hub by default) |
| `docker logout` | Logs out of a registry |
| `docker search centos` | Searches Docker Hub for images |
| `docker push username/image` | Uploads a local image to a registry |
| `docker run -p 5000:5000 registry` | Runs your own private local registry |
| `docker tag image localhost:5000/image` | Tags an image for pushing to a private registry |

---

## 12. Docker Networking

| Command | What It Does |
|---|---|
| `docker network create mynetwork` | Creates a new custom network |
| `docker network ls` | Lists all networks |
| `docker network connect` | Connects a container to a network |
| `docker network disconnect` | Disconnects a container from a network |
| `docker run -p 8080:80 ...` | Maps a host port to a container port |

---

## 13. Docker Volumes

| Command | What It Does |
|---|---|
| `docker volume create` | Creates a new volume |
| `docker volume ls` | Lists volumes |
| `docker volume inspect` | Shows details about a volume |
| `docker volume rm` | Deletes a volume |
| `docker run -v /volume1 ...` | Creates and mounts a volume inside a container |
| `docker run -v /host/path:/container/path ...` | Mounts a folder from the host into the container |

---

## 14. Dockerfile — Key Instructions

| Instruction | What It Does |
|---|---|
| `FROM` | Sets the base image to build on top of |
| `MAINTAINER` | Sets the author of the image (older, mostly replaced by `LABEL`) |
| `RUN` | Runs a command while building the image (e.g. installing packages) |
| `CMD` | Sets the default command to run when the container starts |
| `LABEL` | Adds metadata to the image |
| `EXPOSE` | Documents which network port(s) the container listens on |
| `ENV` | Sets an environment variable |
| `ADD` | Copies files/folders (or remote URLs) into the image |
| `COPY` | Copies local files/folders into the image |
| `ENTRYPOINT` | Configures the container to run as a fixed executable |
| `VOLUME` | Creates a mount point for external/persistent storage |
| `USER` | Sets which user runs the container |
| `WORKDIR` | Sets the working directory for later instructions |
| `ARG` | Defines a build-time variable (`--build-arg`) |
| `ONBUILD` | Adds an instruction that runs later, when this image is used as a base for another |
| `STOPSIGNAL` | Sets which signal is sent to stop the container |

### Example Dockerfile (Nginx static site)

```dockerfile
FROM ubuntu:20.04
RUN apt-get update
RUN apt-get install nginx -y
COPY index.html /var/www/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Building and Running It

| Step | Command |
|---|---|
| Build the image | `docker build -t my-nginx .` |
| Run the container | `docker run -p 80:80 --name my-nginx-01 my-nginx` |
| View the site | Open `http://localhost:80` in a browser |

---

## 15. Quick End-to-End Example (Python Web Server)

| Step | Command |
|---|---|
| Make a folder | `mkdir -p www/` |
| Add a test page | `echo "Server is up" > www/index.html` |
| Run the container | `docker run -d -p 8000:8000 --name=pythonweb -v $(pwd)/www:/var/www/html -w /var/www/html rhel7/rhel /bin/python -m SimpleHTTPServer 8000` |
| Test it | `curl <container-daemon-ip>:8000` |
| Confirm it's running | `docker ps` |
| Inspect it | `docker inspect pythonweb \| less` |
| Look inside | `docker exec -it pythonweb bash` |
