import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse, urljoin, urldefrag

def crawl_and_download(start_url, output_dir="output"):
    """
    Crawls a website, downloads HTML content and images, and saves them to files.
    Ignores <script> and <svg> tags.

    Args:
        start_url (str): The URL to start crawling from.
        output_dir (str): The directory to save the downloaded HTML and images. Defaults to "output".
    """

    visited_urls = set()
    queue = [start_url]
    domain = urlparse(start_url).netloc  # Extract the domain for same-domain crawling
    crawled_urls = []  # List to store successfully crawled URLs
    not_crawled_urls = []  # List to store URLs that were not crawled (404s, etc.)
    image_dir = os.path.join(output_dir, "images")  # Subdirectory for images

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)


    while queue:
        current_url = queue.pop(0)

        # Remove fragment identifier to check for visited URLs
        base_url = urldefrag(current_url).url

        # Avoid crawling external links or already visited links
        if base_url in visited_urls or urlparse(current_url).netloc != domain:
            not_crawled_urls.append(current_url)  # Mark as not crawled (original URL)
            continue

        visited_urls.add(base_url)  # Add the BASE URL to visited_urls
        print(f"Crawling: {current_url}")

        try:
            response = requests.get(current_url, timeout=10)  # Add timeout to prevent hanging
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            html_content = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove script and svg tags
            for script in soup.find_all("script"):
                script.decompose()  # Remove the tag from the tree
            for svg in soup.find_all("svg"):
                svg.decompose()  # Remove the tag from the tree

            # Download images
            download_images(soup, current_url, image_dir)

            # Get the modified HTML content
            html_content = str(soup)  # Convert the soup back to a string

            # Add the URL to the top of the HTML content
            html_content = f"<!-- URL: {current_url} -->\n" + html_content

            # Save the HTML content to a file
            filename = sanitize_filename(current_url, domain)
            filepath = os.path.join(output_dir, filename + ".html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Downloaded: {current_url} to {filepath}")
            crawled_urls.append(current_url) # Add URL to crawled list

            # Extract links from the HTML content
            # Need to re-parse the HTML to ensure that the links are still valid
            soup = BeautifulSoup(html_content, "html.parser")
            for link in soup.find_all("a"):
                href = link.get("href")
                if href:
                    absolute_url = urljoin(current_url, href) # Handle relative URLs
                    # Only add HTML pages to the queue
                    if not absolute_url.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf")):
                        queue.append(absolute_url)

        except requests.exceptions.RequestException as e:
            print(f"Error crawling {current_url}: {e}")
            not_crawled_urls.append(current_url) # Add URL to not crawled list

        except Exception as e:
            print(f"An unexpected error occurred while processing {current_url}: {e}")

    # Write the lists to files
    with open(os.path.join(output_dir, "crawled_urls.txt"), "w", encoding="utf-8") as f:
        for url in crawled_urls:
            f.write(url + "\n")

    with open(os.path.join(output_dir, "not_crawled_urls.txt"), "w", encoding="utf-8") as f:
        for url in not_crawled_urls:
            f.write(url + "\n")

    print("\nCrawling complete!")
    print(f"Crawled URLs saved to: {os.path.join(output_dir, 'crawled_urls.txt')}")
    print(f"Not crawled URLs saved to: {os.path.join(output_dir, 'not_crawled_urls.txt')}")
    print(f"Images saved to: {image_dir}")


def download_images(soup, base_url, image_dir):
    """
    Downloads images from a BeautifulSoup object.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML.
        base_url (str): The base URL of the page.
        image_dir (str): The directory to save the images.
    """
    for img in soup.find_all("img"):
        img_url = img.get("src")
        if img_url:
            absolute_url = urljoin(base_url, img_url)
            try:
                response = requests.get(absolute_url, stream=True, timeout=10)
                response.raise_for_status()

                # Get the filename from the URL, preserving extension
                filename = os.path.basename(urlparse(absolute_url).path)
                filepath = os.path.join(image_dir, filename)

                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded image: {absolute_url} to {filepath}")
            except requests.exceptions.RequestException as e:
                print(f"Error downloading image {absolute_url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing image {absolute_url}: {e}")


def sanitize_filename(url, domain):
    """
    Sanitizes a URL to create a valid and readable filename.

    Args:
        url (str): The URL to sanitize.
        domain (str): The domain name (used to remove it from the filename).

    Returns:
        str: A sanitized filename.
    """
    # Remove protocol (http/https)
    url = url.replace("http://", "").replace("https://", "")

    # Remove domain
    url = url.replace(domain, "")

    # Remove trailing slash
    if url.endswith("/"):
        url = url[:-1]

    # Replace invalid characters with underscores
    url = "".join(c if c.isalnum() or c in ["_", "-", "."] else "_" for c in url)

    # If the sanitized URL is empty, use "index"
    if not url:
        return "index"

    return url


if __name__ == "__main__":
    start_url = input("Enter the URL to crawl: ")
    parsed_url = urlparse(start_url)
    domain = parsed_url.netloc
    default_folder_name = domain.split('.')[1] if len(domain.split('.')) > 1 else domain  # Extract "example" from "www.example.com"

    output_directory = input(f"Enter the output folder name (default: {default_folder_name}): ")
    if not output_directory:
        output_directory = default_folder_name

    crawl_and_download(start_url, output_directory)
    print("Crawling complete!")