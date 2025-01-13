import requests
from bs4 import BeautifulSoup
import os
import time
import socket
import logging
from urllib.parse import urlparse
import ipaddress

# Setup logging to log to a file and also output logs to terminal
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see more details in the terminal
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scrape_diversity_policies.log"),  # Log to file
        logging.StreamHandler()  # Log to terminal (console)
    ]
)

def is_valid_ip(url):
    """
    Validates if the given URL resolves to an IP address.
    Returns True if it resolves to an IP address, False otherwise.
    """
    try:
        hostname = urlparse(url).hostname
        # Try to resolve the hostname to an IP address
        socket.gethostbyname(hostname)
        logging.info(f"Valid IP address found for: {hostname}")
        return True
    except (socket.gaierror, AttributeError):
        logging.warning(f"Invalid URL or unable to resolve IP address: {url}")
        return False

def load_country_data(file_path):
    """
    Loads country-policy data from the specified file.
    Returns a list of country-policy pairs (country_name: policy_name [url]).
    """
    with open(file_path, "r") as f:
        countries = f.readlines()
    return [line.strip() for line in countries if line.strip()]

def fetch_policy_data(url):
    """
    Fetches and extracts policy data from the given URL.
    Returns the policy data (e.g., page title) or None in case of an error.
    """
    if not is_valid_ip(url):
        logging.error(f"Invalid URL: {url}")
        return None

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example: Extracting the title of the page (adjust as needed)
        title = soup.find('title').get_text()
        logging.info(f"Successfully fetched policy data from {url}")
        return title
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def main():
    """
    Main function to process the country-policy data and fetch policy information.
    Outputs results to 'output.txt' and logs the process.
    """
    countries_file = "countries_list.txt"
    countries = load_country_data(countries_file)

    with open("output.txt", "w") as output_file:
        for country_entry in countries:
            try:
                # Split each line into country and policy information
                country_name, policy_info = country_entry.split(":", 1)
                # Extracting multiple policy names and URLs from the same line
                policies = policy_info.split(", ")

                for policy in policies:
                    # Extract the policy name and URL
                    policy_name, url = policy.split(" [", 1)
                    url = url.rstrip("]")  # Remove the closing bracket

                    print(f"Processing {country_name} - {policy_name}...")
                    policy_data = fetch_policy_data(url)

                    if policy_data:
                        output_file.write(f"{country_name} - {policy_name}: {policy_data}\n")
                    else:
                        output_file.write(f"{country_name} - {policy_name}: Error fetching data\n")

                    time.sleep(2)  # Sleep to avoid overwhelming the server (adjust if needed)

            except ValueError as e:
                logging.error(f"Error processing line: {country_entry}. {e}")

    print("Process completed! Check 'output.txt' for the results and 'scrape_diversity_policies.log' for detailed logs.")

if __name__ == "__main__":
    main()