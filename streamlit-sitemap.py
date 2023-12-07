import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO

# Streamlit app title
st.title('VMware KB XML Sitemap Checker')

# File uploader and text input for KB IDs
uploaded_file = st.file_uploader("Upload a file with KB article IDs", type=['txt'])
ids_input = st.text_area("Or enter KB article IDs manually (separate by comma)")

# Define a function to fetch and cache sitemap URLs
@st.cache(show_spinner=False)
def fetch_sitemap_urls(url_prefix, headers):
    response = requests.get(url_prefix, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'xml')
        return [element.text for element in soup.find_all('loc')]
    else:
        raise Exception(f"Error {response.status_code} accessing sitemap index.")

# Define URL prefix and headers for HTTP requests
url_prefix = "https://kb.vmware.com/km_sitemap_index"
headers = {"VMW-Visitor-ID": "kbdev-J7Hm528k9"}

# Attempt to fetch and display the sitemap URLs
try:
    sitemap_urls = fetch_sitemap_urls(url_prefix, headers)
    st.write(f"{len(sitemap_urls)} sitemaps found.")

    for sitemap_url in sitemap_urls:
        response = requests.get(sitemap_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            urls = [element.text for element in soup.find_all('loc')]
            st.write(f"{len(urls)} URLs found in {sitemap_url}")
        else:
            st.error(f"Error {response.status_code} for sitemap {sitemap_url}")
except Exception as e:
    st.error(e)

# File uploader and text input for KB IDs
#uploaded_file = st.file_uploader("Upload a file with KB article IDs", type=['txt'])
#ids_input = st.text_area("Or enter KB article IDs manually (separate by comma)")

# Initialize KB IDs list
kb_ids = []

# Process uploaded file or text input to get KB IDs
if uploaded_file is not None:
    kb_ids = [str(int(line.strip())) for line in uploaded_file]
elif ids_input:
    kb_ids = ids_input.split(',')

# ...

# ...

# Processing KB IDs
if kb_ids and any(id.strip() for id in kb_ids):
    results = []

    # Check each KB ID across all sitemap URLs
    for kb_id in kb_ids:
        kb_id = kb_id.strip()  # Remove any surrounding whitespace from the KB ID
        if kb_id:
            id_found = False  # Initialize the flag as False for each KB ID
            for sitemap_url in sitemap_urls:
                response = requests.get(sitemap_url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    urls = [element.text for element in soup.find_all('loc')]

                    # Check if the current KB ID is found within the current sitemap
                    for url in urls:
                        # Check if the KB ID is a discrete segment in the URL
                        if f"/s/article/{kb_id}" in url or (url.endswith(kb_id) and url[-len(kb_id) - 2] == '/'):
                            id_found = True  # Set the flag to True since we found the ID
                            kb_article_url = url
                            results.append((kb_id, "true", sitemap_url, kb_article_url))
                            st.write(f"ID {kb_id} found: true in {sitemap_url}")
                            break  # Stop searching as we've found the ID
                    if id_found:
                        break  # Break again since we've found the ID and recorded the sitemap

                else:
                    st.error(f"Error {response.status_code} for sitemap {sitemap_url}")

            if not id_found:
                # If the ID was not found in any sitemap, record with a "false" status
                results.append((kb_id, "false", "Not found in any sitemap", "N/A"))
                st.write(f"ID {kb_id} not in any sitemap")

    # Create a CSV file in memory
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["KB id", "True/False", "Sitemap URL", "KB Article URL"])
    for result in results:
        writer.writerow(result)

    # Provide a download link for the CSV file
    st.download_button(
        label="Download Results as CSV",
        data=csv_buffer.getvalue(),
        file_name='results.csv',
        mime='text/csv',
    )
