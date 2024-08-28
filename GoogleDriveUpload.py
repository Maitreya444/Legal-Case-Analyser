import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def authenticate(SCOPES, SERVICE_ACCOUNT_FILE):
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def OpenFiles(directory):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            files.append(file_path)
    return files

def load_uploaded_files(log_file):
    if not os.path.exists(log_file):
        return set()
    
    with open(log_file, 'r') as f:
        uploaded_files = set(line.strip() for line in f)
    return uploaded_files

def log_uploaded_file(log_file, filename):
    with open(log_file, 'a') as f:
        f.write(f"{filename}\n")

def upload(file_path, PARENT_FOLDER_ID, log_file):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    creds = authenticate(SCOPES, SERVICE_ACCOUNT_FILE)
    service = build('drive', 'v3', credentials=creds)

    filename = os.path.basename(file_path)
    
    if filename in uploaded_files:
        print(f"{filename} has already been uploaded. Skipping.")
        return

    file_metadata = {
        'name': filename, 
        'parents': [PARENT_FOLDER_ID]
    }
    
    media = MediaFileUpload(file_path)

    file = service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()

    print(f"Uploaded {filename} with file ID: {file.get('id')}")
    log_uploaded_file(log_file, filename)

def main():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    #Use your Folder id.
    PARENT_FOLDER_ID = "#########"
    #Your path which contains summarised files
    directory = r'C:\Users\DELL\OneDrive\Desktop\FINAL\Bailisummaryoutput'
    log_file = 'log.txt'

    global uploaded_files
    uploaded_files = load_uploaded_files(log_file)

    files = OpenFiles(directory)

    for file_path in files:
        upload(file_path, PARENT_FOLDER_ID, log_file)

if __name__ == "__main__":
    main()
