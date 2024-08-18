import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import csv

def ReadFile(directory):
    print("Reading Files from the directory")
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            files.append(file_path)
    return files

def SendMail(fromaddr, toaddr, Files):

    print("Sending Email")
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = ", ".join(toaddr)  # Convert list to string
    msg['Subject'] = "Baili Case Summarised"
    body = "These attachments are baili cases summarised"

    msg.attach(MIMEText(body, 'plain'))

    try:
        for filepath in Files:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as attachment:
                p = MIMEBase('application', 'octet-stream')
                p.set_payload(attachment.read())

            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename={filename}")
            msg.attach(p)

    except Exception as e:
        print(f"Could not open file {e}")

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(fromaddr, "uwqqlgdepwzeltab")  
        text = msg.as_string()
        s.sendmail(fromaddr, toaddr, text)
        s.quit()
    except Exception as e:
        print(f"Could not send email {e}")

    print("Ending Email function")

def Reciever(csv_path):

    try:
        print("Reading EMAIL-id's from the csv file..")
        mails = []

        with open (csv_path, mode = 'r') as file:
            csv_reader = csv.reader(file)

            for row in csv_reader:
                mails.append(row[0])

        return mails
    
    except Exception as e:
        print(f"Could not send email {e}")

def main():
    toaddr = []

    fromaddr = "gangurdemaitreya@gmail.com"
    csv_path = r'C:\Users\DELL\OneDrive\Desktop\FINAL\Emails.csv'
    toaddr.extend(Reciever(csv_path))
    directory = r"C:\Users\DELL\OneDrive\Desktop\FINAL\Bailisummaryoutput"

    log_file_path = os.path.join(directory, 'EmailLog.log')
    os.makedirs(directory, exist_ok=True)

    processed_files = set()
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            processed_files = set(log_file.read().splitlines())

    files = ReadFile(directory)
    
    files_to_send = [f for f in files if f not in processed_files]
    
    if files_to_send:
        SendMail(fromaddr, toaddr, files_to_send)
        
        # Update log file with newly processed files
        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            for file in files_to_send:
                log_file.write(file + '\n')
    else:
        print("No new files to process.")

if __name__ =="__main__":
    main()
