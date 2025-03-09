# Mailbox Size Report Script - mailbox.v3.local.py

## Overview

This script fetches and displays mailbox sizes for all cPanel accounts using the WHM API. It allows users to sort, filter, and export mailbox size data efficiently.

## Features

- Retrieves all cPanel users and their email accounts.
- Fetches mailbox sizes using WHM API.
- Displays results in a structured format.
- Supports sorting and filtering options.
- Allows exporting results to a CSV file.

## Installation

Ensure Python 3 is installed and the required modules are available. Missing modules will prompt an install request.

Required modules:

- `pandas`
- `tabulate`

If a module is missing, the script will ask for permission to install it.

## Usage

Run the script using the following command:

```sh
python3 mailbox.v3.local.py [OPTIONS]
```

### Command Line Options

| Option         | Description                                                                     |
| -------------- | ------------------------------------------------------------------------------- |
| `-s`           | Sort mailboxes by `total_size`, `mailbox`, or `domain` (default: `total_size`). |
| `-t`           | Display only the top X largest mailboxes.                                       |
| `-u`           | Filter results for specific cPanel users (comma-separated).                     |
| `-o`           | Output results to a CSV file.                                                   |
| `--hide-empty` | Hide mailboxes with zero storage.                                               |

### Example Commands

1. Display all mailbox sizes sorted by total size:

   ```sh
   python3 mailbox.v3.local.py
   ```

2. Show top 10 largest mailboxes:

   ```sh
   python3 mailbox.v3.local.py -t 10
   ```

3. Filter results for specific users:

   ```sh
   python3 mailbox.v3.local.py -u user1,user2
   ```

4. Export results to a CSV file:

   ```sh
   python3 mailbox.v3.local.py -o output.csv
   ```

5. Hide empty mailboxes:

   ```sh
   python3 mailbox.v3.local.py --hide-empty
   ```

## Output Example

The script provides structured output, displaying sorted results per user and domain. Here is an anonymized example:

```
-------- Account: torusco (Total: 171.71 MB) --------

📂 Domain: exampledomain1.com (Total: 41.04 KB)
+---------------+------------------------+----------------+--------------+--------------+
| cPanel_User   | Email                  | Domain         |   Size_Bytes | Size_Human   |
+===============+========================+================+==============+==============+
| torusco       | user1@exampledomain1.com |        42028 | 41.04 KB     |
+---------------+------------------------+----------------+--------------+--------------+
+---------------+---------+----------+--------------+--------------+
| cPanel_User   | Email   | Domain   | Size_Bytes   | Size_Human   |
+===============+=========+==========+==============+==============+
| Total         |         |          | 42,028       | 41.04 KB     |
+---------------+---------+----------+--------------+--------------+

📂 Domain: exampledomain2.com (Total: 171.67 MB)
+---------------+------------------------------------+---------------------------+--------------+--------------+
| cPanel_User   | Email                              | Domain                    |   Size_Bytes | Size_Human   |
+===============+====================================+===========================+==============+==============+
| torusco       | user2@exampledomain2.com    | exampledomain2.com |     76848079 | 73.29 MB     |
+---------------+------------------------------------+---------------------------+--------------+--------------+
| torusco       | user3@exampledomain2.com  | exampledomain2.com |     61769703 | 58.91 MB     |
+---------------+------------------------------------+---------------------------+--------------+--------------+
| torusco       | user4@exampledomain2.com    | exampledomain2.com |     19675191 | 18.76 MB     |
+---------------+------------------------------------+---------------------------+--------------+--------------+
| torusco       | user5@exampledomain2.com    | exampledomain2.com |     18873203 | 18.00 MB     |
+---------------+------------------------------------+---------------------------+--------------+--------------+
| torusco       | user6@exampledomain2.com     | exampledomain2.com |      2273407 | 2.17 MB      |
+---------------+------------------------------------+---------------------------+--------------+--------------+
| torusco       | user7@exampledomain2.com | exampledomain2.com |       573115 | 559.68 KB    |
+---------------+------------------------------------+---------------------------+--------------+--------------+
+---------------+---------+----------+--------------+--------------+
| cPanel_User   | Email   | Domain   | Size_Bytes   | Size_Human   |
+===============+=========+==========+==============+==============+
| Total         |         |          | 180,012,698  | 171.67 MB    |
+---------------+---------+----------+--------------+--------------+

Execution Time: 4.21 seconds
Server: cp.alienpark.com
Total Mailboxes Processed: 68
```

## Notes

- The script must be run on a server with WHM API access.
- Ensure proper API permissions are granted for WHM commands.
- Execution time varies based on the number of mailboxes.

## Contact

For support or issues, please contact the script author.

