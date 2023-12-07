import streamlit as st  # Import Streamlit for web app creation
import requests  # Import requests to make HTTP requests
from bs4 import BeautifulSoup  # Import BeautifulSoup for parsing HTML/XML
import csv  # Import CSV for handling CSV file operations
from io import StringIO  # Import StringIO to handle string-based file-like objects

# Streamlit app title
st.title('VMware KB XML sitemap Checker')  # Set the title of the Streamlit web app

# Define URL prefix and headers for HTTP requests
url_prefix = "https://kb.vmware.com/km_sitemap_index"  # Base URL for the sitemap index
headers = {"VMW-Visitor-ID": "kbdev-J7Hm528k9"}  # Custom headers for the HTTP request

# File uploader and text input for KB IDs
uploaded_file = st.file_uploader("Upload a file with KB article IDs", type=['txt'])  # File uploader widget
if uploaded_file is not None:
    # If a file is uploaded, read KB IDs from the file
    kb_ids = [str(int(line.strip())) for line in uploaded_file]  # Parse and store KB IDs from the file
else:
    # If no file is uploaded, use manual text input for KB IDs
    ids_input = st.text_area("Or enter KB article IDs manually (separate by comma)")  # Text area for manual input
    kb_ids = ids_input.split(',')  # Split the input string into a list of KB IDs

# Check if KB IDs are provided and non-empty
if kb_ids and any(id.strip() for id in kb_ids):
    # Make an HTTP request to get the sitemap URLs
    response = requests.get(url_prefix, headers=headers)  # HTTP GET request for the sitemap index
    sitemap_urls = []  # Initialize an empty list to store sitemap URLs

    # Check if the HTTP request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')  # Parse the XML response
        sitemap_urls = [element.text for element in soup.find_all('loc')]  # Extract sitemap URLs from XML
        st.write(f"{len(sitemap_urls)} sitemaps found.")  # Display the number of sitemaps found
    else:
        st.write(f"Error {response.status_code} for page {url_prefix}")  # Display error if HTTP request fails

    results = []  # Initialize an empty list to store the results

    # Iterate over each sitemap URL
    for sitemap_url in sitemap_urls:
            response = requests.get(sitemap_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'xml')
                urls = [element.text for element in soup.find_all('loc')]

                # Display the number of URLs in the current sitemap
                st.write(f"{len(urls)} URLs found in {sitemap_url}")

            # Check each URL for the presence of KB IDs
            for kb_id in kb_ids:
                    if kb_id.strip():  # Check if the KB ID is not just whitespace
                        found = any(url for url in urls if ('/s/article/'+kb_id+'/' in url) or ('/s/article/'+kb_id in url and url.endswith(kb_id)))
                        if found and not any(result for result in results if result[0] == kb_id):
                            results.append((kb_id, "true", sitemap_url))
                            st.write(f"ID {kb_id} found: true in {sitemap_url}")
            else:
                st.error(f"Error {response.status_code} for sitemap {sitemap_url}")

    else:
        st.error(f"Error {response.status_code} for page {url_prefix}")

    # Commented out the redundant check for KB IDs
    # for kb_id in kb_ids:
    #     found = any(url for url in urls if ('/s/article/'+kb_id+'/' in url) or ('/s/article/'+kb_id in url and url.endswith(kb_id)))
    #     if found:
    #         results.append((kb_id, "true", sitemap_url))  # Append result if KB ID is found
    #         st.write(f"ID {kb_id} found: true in {sitemap_url}")  # Display found message
    #     else:
    #         st.write(f"ID {kb_id} not found in {sitemap_url}")  # Display not found message

    # Create a CSV file in memory
    csv_buffer = StringIO()  # Initialize a string
