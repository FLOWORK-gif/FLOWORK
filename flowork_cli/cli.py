#######################################################################
# dev : awenk audico
# EMAIL SAHIDINAOLA@GMAIL.COM
# WEBSITE WWW.TEETAH.ART
# File NAME : C:\FLOWORK\flowork_cli\cli.py
# JUMLAH BARIS : 36
#######################################################################

import sys
import argparse
from .core.api_client import ApiClient
def main():
    """
    The main function for the CLI.
    Now includes argument parsing for different commands.
    """
    parser = argparse.ArgumentParser(description="Flowork Command-Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    parser_status = subparsers.add_parser("status", help="Check the connection status to the Flowork API server.")
    args = parser.parse_args()
    print("--- Flowork CLI Initializing ---")
    api = ApiClient()
    if args.command == "status":
        print("Attempting to connect to Flowork server...")
        success, response = api.get_server_status()
        if success:
            server_status = response.get('status', 'unknown')
            kernel_version = response.get('version', 'N/A')
            print(f"✅ Connection successful!")
            print(f"   Server Status: {server_status}")
            print(f"   Kernel Version: {kernel_version}")
        else:
            print(f"❌ Connection failed: {response}")
            sys.exit(1)
    else:
        print("No command provided. Use 'status' to check server connection.")
        print("Example: poetry run python -m flowork_cli status")
