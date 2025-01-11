import pkg_resources

# Get the version of Web3.py
web3_version = pkg_resources.get_distribution("web3").version
print(f"Web3.py version: {web3_version}")
