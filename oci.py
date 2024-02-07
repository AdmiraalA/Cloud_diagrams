import subprocess
import sys

# Check Python version
if sys.version_info[0] < 3:
    print("This script requires Python 3 or later.")
    sys.exit(1)

# Check if OCI SDK is installed, if not, install it
try:
    import oci
except ImportError:
    print("OCI SDK not found. Installing...")
    if sys.version_info[0] == 2:
        subprocess.call(['pip2', 'install', 'oci'])
    else:
        subprocess.call(['pip3', 'install', 'oci'])
    print("OCI SDK installed successfully!")

from diagrams import Diagram, Cluster
from diagrams.oci.compute import Compute, Instance
from diagrams.oci.database import Database, DatabaseSystem
from diagrams.oci.network import LoadBalancer
from diagrams.oci.storage import ObjectStorage

# Initialize OCI SDK
def initialize_oci_sdk():
    config = oci.config.from_file("~/.oci/config")
    identity = oci.identity.IdentityClient(config)
    return identity

# Function to fetch all compartments in the tenancy
def get_compartments(identity):
    compartments = {}
    for compartment in identity.list_compartments(config["tenancy"]).data:
        compartments[compartment.id] = compartment.name
    return compartments

# Function to fetch all resources in a compartment
def get_resources(identity, compartment_id):
    resources = {}
    # Fetch compute instances
    compute_instances = identity.list_instances(compartment_id).data
    resources["ComputeInstances"] = compute_instances
    # Fetch databases
    databases = identity.list_db_systems(compartment_id).data
    resources["Databases"] = databases
    # Fetch load balancers
    load_balancers = identity.list_load_balancers(compartment_id).data
    resources["LoadBalancers"] = load_balancers
    # Fetch object storage
    object_storage = identity.list_buckets(compartment_id).data
    resources["ObjectStorage"] = object_storage
    return resources

# Function to generate diagram
def generate_diagram(resources):
    with Diagram("OCI Resources", show=False):
        with Cluster("Compute"):
            for instance in resources["ComputeInstances"]:
                Instance(instance.display_name)
        with Cluster("Databases"):
            for db in resources["Databases"]:
                DatabaseSystem(db.display_name)
        with Cluster("Networking"):
            for lb in resources["LoadBalancers"]:
                LoadBalancer(lb.display_name)
        with Cluster("Object Storage"):
            for bucket in resources["ObjectStorage"]:
                ObjectStorage(bucket.name)

# Main function
def main():
    identity = initialize_oci_sdk()
    compartments = get_compartments(identity)
    for compartment_id, compartment_name in compartments.items():
        print(f"Fetching resources in compartment: {compartment_name}")
        resources = get_resources(identity, compartment_id)
        generate_diagram(resources)
        print(f"Diagram generated successfully for compartment: {compartment_name}")

if __name__ == "__main__":
    main()
