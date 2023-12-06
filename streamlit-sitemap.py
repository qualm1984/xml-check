import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO

# Streamlit app title
st.title('VMware KB XML sitemap Checker')

# Define URL prefix and headers
url_prefix = "https://kb.vmware.com/km_sitemap_index"
headers = {"VMW-Visitor-ID": "kbdev-J7Hm528k9"}

# File uploader and text input for KB IDs
uploaded_file = st.file_uploader("Upload a file with KB article IDs", type=['txt'])
if uploaded_file is not None:
    kb_ids = [str(int(line.strip())) for line in uploaded_file]
else:
    ids_input = st.text_area("Or enter KB article IDs manually (separate by comma)")
    kb_ids = ids_input.split(',')



if kb_ids:
    # Get the sitemap URLs
    response = requests.get(url_prefix, headers=headers)
    sitemap_urls = []

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        sitemap_urls = [element.text for element in soup.find_all('loc')]
        st.write(f"{len(sitemap_urls)} sitemaps found.")
    else:
        st.write(f"Error {response.status_code} for page {url_prefix}")

    results = []

    # Go through each sitemap URL and get the URLs within it
    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            urls = [element.text for element in soup.find_all('loc')]
            st.write(f"{len(urls)} URLs found in {sitemap_url}")

            # Go through all the URLs in current sitemap and check for the IDs
            for kb_id in kb_ids:
                found = any(url for url in urls if ('/s/article/'+kb_id+'/' in url) or ('/s/article/'+kb_id in url and url.endswith(kb_id)))
                if found and not any(result for result in results if result[0] == kb_id):
                    results.append((kb_id, "true", sitemap_url))
                    st.write(f"ID {kb_id} found: true in {sitemap_url}")
        else:
            st.write(f"Error {response.status_code} for sitemap {sitemap_url}")


    for kb_id in kb_ids:
        found = any(url for url in urls if ('/s/article/'+kb_id+'/' in url) or ('/s/article/'+kb_id in url and url.endswith(kb_id)))
        if found:
            results.append((kb_id, "true", sitemap_url))
            st.write(f"ID {kb_id} found: true in {sitemap_url}")
        else:
            st.write(f"ID {kb_id} not found in {sitemap_url}")

            # Write results to a CSV file
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["KB id", "True/False", "Sitemap URL"])
    for result in results:
        writer.writerow(result)

    # Provide download link for the CSV
    st.download_button(
        label="Download Results as CSV",
        data=csv_buffer.getvalue(),
        file_name='results.csv',
        mime='text/csv',
    )