import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO

# Streamlit app title
st.title('VMware KB XML sitemap Checker')

# File uploader and text input for KB IDs
uploaded_file = st.file_uploader("Upload a file with KB article IDs", type=['txt'])
if uploaded_file is not None:
    kb_ids = [str(int(line.strip())) for line in uploaded_file]
else:
    ids_input = st.text_area("Or enter KB article IDs manually (separate by comma)")
    kb_ids = ids_input.split(',')


# Define URL prefix and headers for HTTP requests
url_prefix = "https://kb.vmware.com/km_sitemap_index"
headers = {"VMW-Visitor-ID": "kbdev-J7Hm528k9"}

# Make an HTTP request to get the sitemap URLs
response = requests.get(url_prefix, headers=headers)
sitemap_urls = []

# Check if the HTTP request was successful
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'xml')
    sitemap_urls = [element.text for element in soup.find_all('loc')]
    st.write(f"{len(sitemap_urls)} sitemaps found.")

    # Displaying the number of URLs in each sitemap
    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            urls = [element.text for element in soup.find_all('loc')]
            st.write(f"{len(urls)} URLs found in {sitemap_url}")
        else:
            st.error(f"Error {response.status_code} for sitemap {sitemap_url}")
else:
    st.error(f"Error {response.status_code} for page {url_prefix}")

# Processing KB IDs
if kb_ids and any(id.strip() for id in kb_ids):
    # Make an HTTP request to get the sitemap URLs
    response = requests.get(url_prefix, headers=headers)
    sitemap_urls = []

    # Check if the HTTP request was successful
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')  # Parse the XML response
        sitemap_urls = [element.text for element in soup.find_all('loc')]  # Extract sitemap URLs from XML
        st.write(f"{len(sitemap_urls)} sitemaps found.")  # Display the number of sitemaps found

        # Initialize an empty list to store the results
        results = []  

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

        # Create a CSV file in memory
        csv_buffer = StringIO()  # Initialize a string buffer for the CSV file
        writer = csv.writer(csv_buffer)  # Create a CSV writer object
        writer.writerow(["KB id", "True/False", "Sitemap URL"])  # Write the header row to the CSV file
        for result in results:
            writer.writerow(result)  # Write each result to the CSV file

        # Provide a download link for the CSV file
        st.download_button(
            label="Download Results as CSV",
            data=csv_buffer.getvalue(),
            file_name='results.csv',
            mime='text/csv',
        )  # Streamlit widget to download the CSV file

    else:
        # Report error only if the status code is not 200
        st.error(f"Error {response.status_code} for page {url_prefix}")