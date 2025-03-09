#!/usr/bin/env python3
"""
Mailbox Size Report Script - Version V3
Description: Fetches and displays mailbox sizes for all cPanel accounts using WHM API.
"""

import sys
import subprocess
import importlib

# Required modules list
REQUIRED_MODULES = ["pandas", "tabulate"]

# Function to check and install missing modules
def check_and_install_modules():
    missing_modules = []

    for module in REQUIRED_MODULES:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("\n\033[1;31mMissing required modules:\033[0m", ", ".join(missing_modules))
        for module in missing_modules:
            while True:
                choice = input(f"Would you like to install '\033[1;32m{module}\033[0m'? (y/n): ").strip().lower()
                if choice == "y":
                    print(f"\nInstalling {module}...\n")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                    break
                elif choice == "n":
                    print("\n\033[1;31mRequired module missing. Aborting.\033[0m")
                    sys.exit(1)
                else:
                    print("\033[1;31mInvalid input. Please enter 'y' or 'n'.\033[0m")

        # Reload newly installed modules
        for module in missing_modules:
            importlib.import_module(module)

# Run module check before importing third-party modules
check_and_install_modules()

# Now it's safe to import third-party modules
import json
import argparse
import pandas as pd
import time
import socket
from tabulate import tabulate

# Function to run WHM API commands locally
def run_whmapi(command):
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        data = json.loads(result.stdout)

        if not data or "error" in data:
            return None

        return data
    except json.JSONDecodeError:
        return None

# Function to get all cPanel users locally
def get_cpanel_users():
    data = run_whmapi("whmapi1 listaccts --output=json")
    if not data or "data" not in data or "acct" not in data["data"]:
        print("\033[1;31mError: No cPanel users found.\033[0m")
        sys.exit(1)
    
    return [user["user"] for user in data["data"]["acct"]]

# Function to fetch mailboxes for a user locally
def get_mailboxes(user):
    data = run_whmapi(f"uapi --user={user} Email list_pops_with_disk --output=json")
    if not data or "result" not in data or "data" not in data["result"]:
        return []

    return data["result"]["data"]

# Function to convert bytes to a human-readable format
def convert_to_human(size_bytes):
    size_bytes = int(size_bytes)
    if size_bytes >= 1024**4:
        return f"{size_bytes / (1024**4):.2f} TB"
    elif size_bytes >= 1024**3:
        return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= 1024**2:
        return f"{size_bytes / (1024**2):.2f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes} B"

# Function to collect all mailboxes
def collect_mailboxes(users, hide_empty=False):
    mailbox_data = []
    for user in users:
        mailboxes = get_mailboxes(user)
        if not mailboxes:
            continue

        for mailbox in mailboxes:
            email = mailbox["email"]
            domain = mailbox["domain"]
            size_bytes = int(float(mailbox.get("_diskused", 0)))

            if hide_empty and size_bytes == 0:
                continue  # Skip empty mailboxes if --hide-empty is used

            size_human = convert_to_human(size_bytes)
            mailbox_data.append([user, email, domain, size_bytes, size_human])

    return mailbox_data

# Function to display output with sorted accounts
def display_results(mailbox_data, sort_by, top_x=None, output_file=None):
    df = pd.DataFrame(mailbox_data, columns=["cPanel_User", "Email", "Domain", "Size_Bytes", "Size_Human"])
    df["Size_Bytes"] = df["Size_Bytes"].astype(int)

    if df.empty:
        print("\033[1;31mNo mailboxes found.\033[0m")
        sys.exit(1)

    if top_x:
        df = df.sort_values(by="Size_Bytes", ascending=False).head(top_x)
        print("\n\033[1;34mTop {} Largest Mailboxes Across All Accounts\033[0m".format(top_x))
        print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
    else:
        print("\n\033[1;34mMailbox Sizes for All cPanel Users (Sorted by Account and Domain)\033[0m")

        # ✅ Sorting logic
        if sort_by == "mailbox":
            account_totals = df.groupby("cPanel_User")["Size_Bytes"].max().reset_index()
        elif sort_by == "domain":
            account_totals = df.groupby(["cPanel_User", "Domain"])["Size_Bytes"].sum().reset_index()
            account_totals = account_totals.groupby("cPanel_User")["Size_Bytes"].max().reset_index()
        else:
            account_totals = df.groupby("cPanel_User")["Size_Bytes"].sum().reset_index()

        account_totals = account_totals.sort_values(by="Size_Bytes", ascending=False)

        for _, row in account_totals.iterrows():
            user = row["cPanel_User"]
            user_df = df[df["cPanel_User"] == user]
            account_total_bytes = row["Size_Bytes"]
            account_total_human = convert_to_human(account_total_bytes)

            print(f"\n\033[1;33m-------- Account: {user} (Total: {account_total_human}) --------\033[0m")

            domain_totals = user_df.groupby("Domain")["Size_Bytes"].sum().reset_index()
            for _, domain_row in domain_totals.iterrows():
                domain = domain_row["Domain"]
                domain_df = user_df[user_df["Domain"] == domain]
                domain_df = domain_df.sort_values(by="Size_Bytes", ascending=False)

                total_bytes = domain_df["Size_Bytes"].sum()
                total_human = convert_to_human(total_bytes)

                print(f"\n\033[1;36m📂 Domain: {domain} (Total: {total_human})\033[0m")
                print(tabulate(domain_df, headers="keys", tablefmt="grid", showindex=False))

                # ✅ Properly formatted total row (without domain)
                total_row = [["Total", "", "", f"{total_bytes:,}", total_human]]
                print(tabulate(total_row, headers=["cPanel_User", "Email", "Domain", "Size_Bytes", "Size_Human"], tablefmt="grid"))

    if output_file:
        df.to_csv(output_file, index=False)
        print(f"\n\033[1;32mResults saved to {output_file}\033[0m")

# Main script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch mailbox sizes from WHM locally (Version V3)")
    parser.add_argument("-s", type=str, choices=["total_size", "mailbox", "domain"], default="total_size",
                        help="Sort accounts by total storage, largest mailbox, or largest domain")
    parser.add_argument("-t", type=int, help="Show only the top X largest mailboxes")
    parser.add_argument("-u", type=str, help="Filter results for specific cPanel users (comma-separated)")
    parser.add_argument("-o", type=str, help="Output results as a CSV file")
    parser.add_argument("--hide-empty", action="store_true", help="Hide mailboxes with zero storage")

    args = parser.parse_args()
    start_time = time.time()
    server_name = socket.gethostname()

    users = get_cpanel_users()
    if args.u:
        users = args.u.split(",")

    mailbox_data = collect_mailboxes(users, hide_empty=args.hide_empty)
    display_results(mailbox_data, args.s, top_x=args.t, output_file=args.o)

    print(f"\n\033[1;32mExecution Time:\033[0m {round(time.time() - start_time, 2)} seconds")
    print(f"\033[1;32mServer:\033[0m {server_name}")
    print(f"\033[1;32mTotal Mailboxes Processed:\033[0m {len(mailbox_data)}")
