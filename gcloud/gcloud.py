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
SERVICE_ACCOUNT_NAME = "europe-west1-b"
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
    f"setsid -f python3 {APP_PATH}/productpage_monolith.py {APP_PORT}",
]

def init():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

def get_zones():
    try:
        cmd = "gcloud compute zones list"
        proc = sp.run(
            cmd.split(" "), stdout=sp.PIPE, stderr=sp.STDOUT
        )
        proc.check_returncode()
        zones = proc.stdout.decode("utf-8")
        return zones.split("\n")[1:-1]
    except sp.CalledProcessError:
        exit(0)


def create():
    try:
        cmd = f"gcloud compute instances create {INSTANCE_NAME} --project={PROJECT_ID} --zone={INSTANCE_ZONE} --machine-type=e2-medium --network-interface=network-tier=PREMIUM,subnet=default --maintenance-policy=MIGRATE --service-account={SERVICE_ACCOUNT_NAME}@{PROJECT_ID}.iam.gserviceaccount.com --scopes=https://www.googleapis.com/auth/cloud-platform --tags=http-server,https-server --create-disk=auto-delete=yes,boot=yes,device-name={INSTANCE_NAME},image=projects/debian-cloud/global/images/debian-10-buster-v20211209,mode=rw,size=10,type=projects/{PROJECT_ID}/zones/{INSTANCE_ZONE}/diskTypes/pd-balanced --no-shielded-secure-boot --shielded-vtpm --shielded-integrity-monitoring --reservation-affinity=any"
        proc = sp.run(
            cmd.split(" "), stdout=sp.PIPE, stderr=sp.DEVNULL
        )
        proc.check_returncode()
    except sp.CalledProcessError:
        exit(0)

def list_instances(project_id: str, zones: list) -> typing.Iterable[gcp.Instance]:
    """
    List all instances in the given zone in the specified project.

    Args:
        project_id: project ID or project number of the Cloud project you want to use.
        zone: name of the zone you want to use. For example: “us-west3-b”
    Returns:
        An iterable collection of Instance objects.
    """
    instance_client = gcp.InstancesClient()
    instances = {}
    for zone in zones:
        instances[zone] = instance_client.list(project=project_id, zone=zone)

        print(f"Instances found in zone {zone}:")
        for instance in instances[zone]:
            print(f" - {instance.name} ({instance.machine_type})")

    return instances

def deploy():
    for sh_cmd in DEPLOY_COMMANDS:
        proc = None
        try:
            cmd = f"gcloud compute ssh {INSTANCE_NAME} --zone={INSTANCE_ZONE} --project={PROJECT_ID} --command='{sh_cmd}'"
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
    init()
    if (len(sys.argv) > 1):
        if (sys.argv[1] == "create"):
            create()
        elif (sys.argv[1] == "list"):
            if (len(sys.argv) > 2):
                list_instances(PROJECT_ID, sys.argv[2].split(","))
            else:
                list_instances(PROJECT_ID, [INSTANCE_ZONE])
        elif (sys.argv[1] == "deploy"):
            deploy()
        else:
            print("Invalid command")
    else:
        print("No command specified")

if __name__=="__main__":
    main()
