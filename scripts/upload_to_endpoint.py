import argparse
import os
import sys
import requests
from typing import Optional


def upload_file(
    file_path: str,
    endpoint_url: str,
    auth_key: Optional[str] = None,
    verbose: bool = False
) -> bool:
    """
    Upload a file to a specified endpoint.

    Args:
        file_path: Path to the file to upload
        endpoint_url: URL endpoint to send the file to
        auth_key: Optional authentication key
        verbose: Enable verbose output

    Returns:
        True if upload was successful, False otherwise
    """
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    if verbose:
        print(f"Uploading {file_path} to {endpoint_url}...")

    try:
        headers = {}
        if auth_key:
            headers["Authorization"] = f"Bearer {auth_key}"

        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f)}
            response = requests.post(
                endpoint_url,
                files=files,
                headers=headers,
                timeout=300  # 5 minute timeout
            )

        response.raise_for_status()

        if verbose:
            print(f"Upload successful! Status code: {response.status_code}")
            print(f"Response: {response.text}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error uploading file: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload a file to a specified endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Upload with authentication
  %(prog)s commits_2024-01-01_to_2024-12-31.xlsx -u https://api.example.com/upload -k YOUR_API_KEY

  # Upload without authentication
  %(prog)s commits_2024-01-01_to_2024-12-31.xlsx -u https://api.example.com/upload

  # Verbose output
  %(prog)s commits_2024-01-01_to_2024-12-31.xlsx -u https://api.example.com/upload -k YOUR_API_KEY -v
        """
    )

    parser.add_argument(
        "file",
        help="Path to the file to upload"
    )

    parser.add_argument(
        "-u", "--url",
        required=True,
        help="Endpoint URL to upload the file to"
    )

    parser.add_argument(
        "-k", "--key",
        help="Authentication key (will be sent as 'Bearer' token in Authorization header)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    success = upload_file(
        file_path=args.file,
        endpoint_url=args.url,
        auth_key=args.key,
        verbose=args.verbose
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
