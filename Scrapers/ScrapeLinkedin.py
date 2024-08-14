from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import re

driver = webdriver.Firefox()

driver.get("https://www.linkedin.com/login")

username = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "session_key"))
)
username.send_keys("gangurdemaitreya@gmail.com")

password = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "session_password"))
)
password.send_keys("RyandgpMaitreya")

password.send_keys(Keys.RETURN)

time.sleep(20)

user_profile_url = "https://www.linkedin.com/in/costslawyer/recent-activity/all/"
driver.get(user_profile_url)

time.sleep(20)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

posts = soup.find_all('div', class_='feed-shared-update-v2')

# Check if any posts were found
if not posts:
    print("No posts found. Please check the selector or ensure the page has fully loaded.")

# Create a save directory if it doesn't exist
save_directory = "linkedin_posts"
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)

# Loop through each post and save to a text file if not already saved
for i, post in enumerate(posts, start=1):
    post_content = post.get_text().strip()

    title_tag = post.find('h2')  # Adjust the tag based on the actual HTML structure
    title = title_tag.get_text().strip() if title_tag else f"post_{i}"
    
    # Sanitize title for filename
    sanitized_title = sanitize_filename(title)
    
    # Create a filename for the text
    text_filename = os.path.join(save_directory, f"{sanitized_title}.txt")

    # Check if the file already exists
    if not os.path.exists(text_filename):
        # Write the post content to the file
        with open(text_filename, 'w', encoding='utf-8') as file:
            file.write(post_content)
        
        print(f"Post {i} saved to {text_filename}")
    else:
        print(f"Post {i} already exists, skipping.")

# Close the browser
driver.quit()
