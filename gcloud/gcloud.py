#!/usr/bin/python

# Authors: Samuel García Sánchez and Andrés Álvarez de Cienfuegos

import os, sys
import subprocess as sp
import typing
import google.cloud.compute_v1 as gcp

# Constants
PROJECT_ID = "cdps-creative-2"
INSTANCE_NAME = "instance-1"
INSTANCE_ZONE = "europe-west1-b"
SERVICE_ACCOUNT_NAME = "cdps-2"
GOOGLE_APPLICATION_CREDENTIALS = "./key.json"
APP_PATH = "practica_creativa2/bookinfo/src/productpage"
APP_PORT = "9080"
GROUP_NUMBER = "43"
DEPLOY_COMMANDS = [
    "sudo apt update",
    "sudo apt install -y git python3-pip",
    "rm -rf practica_creativa2",
    "git clone https://github.com/CDPS-ETSIT/practica_creativa2.git",
    f"pip3 install -r {APP_PATH}/requirements.txt",
    "sed -i \"/block\\ title/ s/}.*{/}%s{/\" %s/templates/productpage.html" % (GROUP_NUMBER, APP_PATH),
    f"setsid -f python3 {APP_PATH}/productpage_monolith.py {APP_PORT} > productpage.log 2>&1",
]

def init(credentials: str = GOOGLE_APPLICATION_CREDENTIALS):
    if not os.path.exists(credentials):
        print(f"Error: {credentials} does not exist")
        exit(0)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials

def get_zones(regex: str = None):
    try:
        cmd = "gcloud compute zones list | awk '{print $1}'"
        if regex:
            cmd += f" | grep -E '{regex}'"

        proc = sp.run(
            cmd, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT
        )
        proc.check_returncode()
        zones = proc.stdout.decode("utf-8")
        return zones.split("\n")[1:-1]
    except sp.CalledProcessError:
        exit(0)


def create(
    zone: str = INSTANCE_ZONE,
    name: str = INSTANCE_NAME,
    id: str = PROJECT_ID
):
    print(f"Creating instance {name} in zone {zone} in project {id}")
    try:
        cmd = f"gcloud compute instances create {name} --project={id} --zone={zone} --machine-type=e2-medium --network-interface=network-tier=PREMIUM,subnet=default --maintenance-policy=MIGRATE --service-account={SERVICE_ACCOUNT_NAME}@{id}.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --tags=http-server,https-server --create-disk=auto-delete=yes,boot=yes,device-name={name},image=projects/debian-cloud/global/images/debian-10-buster-v20211209,mode=rw,size=10,type=projects/{id}/zones/{zone}/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any"
        proc = sp.run(
            cmd.split(" "), stdout=sp.PIPE, stderr=sp.DEVNULL
        )
        proc.check_returncode()
    except sp.CalledProcessError:
        exit(0)

def list_instances(project_id: str, zones: list):
    instance_client = gcp.InstancesClient()
    instances = {}
    for zone in zones:
        instances[zone] = instance_client.list(project=project_id, zone=zone)

        print(f"Instances found in zone {zone}:")
        for instance in instances[zone]:
            print(f" - {instance.name} ({instance.machine_type})")

    return instances

def deploy(
    zone: str = INSTANCE_ZONE,
    name: str = INSTANCE_NAME,
    id: str = PROJECT_ID
):
    print("Deploying application to instance {name} in zone {zone} of project {id}")
    for sh_cmd in DEPLOY_COMMANDS:
        proc = None
        try:
            cmd = f"gcloud compute ssh {name} --zone={zone} --project={id} --command='{sh_cmd}'"
            print(f"Executing '{sh_cmd}'")
            proc = sp.run(
                cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE
            )
            proc.check_returncode()
        except sp.CalledProcessError:
            print(f"Error executing command: {sh_cmd}")
            if proc:
                print(f"{proc.stdout.decode('utf-8')}")
                print(f"{proc.stderr.decode('utf-8')}")
            exit(0)

def main():
    if len(sys.argv) > 1:
        # Get arguments
        if "--zone" in sys.argv:
            zone = sys.argv[sys.argv.index("--zone") + 1]
            sys.argv.remove("--zone")
            sys.argv.remove(zone)
        else:
            zone = INSTANCE_ZONE

        if "--name" in sys.argv:
            name = sys.argv[sys.argv.index("--name") + 1]
            sys.argv.remove("--name")
            sys.argv.remove(name)
        else:
            name = INSTANCE_NAME

        if "--id" in sys.argv:
            id = sys.argv[sys.argv.index("--id") + 1]
            sys.argv.remove("--id")
            sys.argv.remove(id)
        else:
            id = PROJECT_ID

        if "--zones" in sys.argv:
            zones_arg = sys.argv[sys.argv.index("--zones") + 1]
            zones = zones_arg.split(",")
            sys.argv.remove("--zones")
            sys.argv.remove(zones_arg)
        elif "--match" in sys.argv:
            regex = sys.argv[sys.argv.index("--match") + 1]
            zones = get_zones(regex)
            sys.argv.remove("--match")
            sys.argv.remove(regex)
        else:
            zones = None
            regex = None

        if "--credentials" in sys.argv:
            credentials = sys.argv[sys.argv.index("--credentials") + 1]
            sys.argv.remove("--credentials")
            sys.argv.remove(credentials)
        else:
            credentials = GOOGLE_APPLICATION_CREDENTIALS

        # Execute commands
        init(credentials)
        if sys.argv[1] == "create":
            create(zone, name, id)
        elif sys.argv[1] == "lszones":
            print("Available zones:")
            if not zones: zones = get_zones()
            for zone in zones:
                print(f" - {zone}")
        elif sys.argv[1] == "list":
            if not zones: zones = get_zones()
            list_instances(id, zones)
        elif (sys.argv[1] == "deploy"):
            deploy(zone, name, id)
        else:
            print("Invalid command")
    else:
        print("No command specified")

if __name__=="__main__":
    main()
