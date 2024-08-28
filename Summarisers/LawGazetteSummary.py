import re
import os
import nltk
import spacy
import pandas as pd
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import language_tool_python

nlp = spacy.load('en_core_web_sm')
nltk.download('punkt')
pd.set_option("display.max_rows", 200)

def OpenFiles(directory):
    try:
        files = []
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                file_path = os.path.join(directory, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    text = file.read()
                    files.append((text, filename))
        return files
    except Exception as e:
        print(f"Exception occurred: {e}")
    return None

def write_to_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Exception occurred: {e}")

def Grammar(content):
    print("Rectifying Punctuation in the summarized text")
    try:
        tool = language_tool_python.LanguageTool('en-GB')
        result = tool.correct(content)
        print("Ending Rectification")
        return result
    except Exception as e:
        print(f"Exception occured : {e}")
        #if exception occured return as it file content
        return content

def FetchCaseName(FileName):
    try:
        print(f"Processing {FileName}")
        return f"Name of File : {FileName}\n\n"
    except Exception as e:
        print(f"Exception occurred: {e}")
    return None

def FetchCourtName(FileText):
    try:
        print("FetchCourtName function started...")
        result = ["\n"]

        if 'High Court' in FileText or 'high court' in FileText:
            print("Found HighCourt")
            result.append("Court Name : HIGH COURT")
        elif 'EWCA' in FileText:
            print("Found EWCA")
            result.append("Court Name : ENGLAND & WALES COURT OF APPEAL")
        elif 'KB' in FileText:
            print("FOUND KB")
            result.append("KING'S BENCH DIVISION")
        elif 'ch' in FileText or 'CH' in FileText:
            print("FOUND CH")
            result.append("CHANCERY DIVISION")
        elif 'SCCO' in FileText:
            print("FOUND SCCO")
            result.append("SENIOR COURT COSTS OFFICE")
        elif 'QB' in FileText or 'qb' in FileText:
            print("FOUND QB")
            result.append("QUEEN'S BENCH DIVISION")

        print("Ending FetchCourtName Function")
        result.append("\n")
        return result
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def QuestionsToTheCourt(FileText):
    try:
        print("Fetching Questions for the Court")
        result = ["\nQuestions For The Court : \n"]
        #result.append("\n")
        pattern = r'Whether\s*(.*?)(?:\.\s|\n|$)'
        matches = re.finditer(pattern, FileText, re.DOTALL | re.IGNORECASE)

        if matches:
            question_number = 1
            for match in matches:
                question = match.group(1).strip()
                if question:
                    result.append("\n")
                    result.append(f"{question_number}. Whether {question}")
                    question_number += 1
            result.append("\n")
        else:
            result.append("Not Found\n")

        print("Ending Fetching questions to the Court")
        result.append("\n")
        return ''.join(result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return ""

def Summary(FileText):
    try:
        print("Summarizing...")

        result0 = ["\n"]
        result1 = ["Summary : \n"]
        result = []
        result.append("\n")

        tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-summarize-news")
        model = AutoModelForSeq2SeqLM.from_pretrained("mrm8488/t5-base-finetuned-summarize-news")

        inputs = tokenizer(FileText, return_tensors="pt", truncation=True, padding=True, max_length=512)
        input_ids = inputs.input_ids
        attention_mask = inputs.attention_mask

        generated_ids = model.generate(
            input_ids=input_ids, 
            attention_mask=attention_mask,
            num_beams=4, 
            max_length=200, 
            repetition_penalty=2.0, 
            length_penalty=1.0, 
            early_stopping=True
        )

        summary = tokenizer.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        result.append(' '.join(summary).strip())
        print("Ending Summary...")
        result.append("\n")
        return ''.join(result0 + result1 + result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def FetchCosts(FileText):
    print("Fetching Costs Started...")
    try:
        print("Now Fetching Costs....")
        doc = nlp(FileText)
        result = ["\nCosts : \n"]
        result.append("\n")

        entities = [(ent.text, ent.start_char, ent.end_char) for ent in doc.ents if ent.label_ == "MONEY"]

        if entities:
            points = 0
            for sent in doc.sents:
                if any(ent[1] >= sent.start_char and ent[2] <= sent.end_char for ent in entities):
                    points += 1
                    result.append("\n")
                    result.append(f"{points}. {sent.text.strip()}")
        else:
            result.append("Costs Not Found")

        print("Ending Fetching Costs")
        result.append("\n")

        return ''.join(result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None
    
def FetchPercent(FileText):
    print("Fetching Percent Started...")
    try:
        print("Now Fetching Percent....")
        doc = nlp(FileText)
        result = ["\nPercent :"]
        result.append("\n")

        entities = [(ent.text, ent.start_char, ent.end_char) for ent in doc.ents if ent.label_ == "PERCENT"]

        if entities:
            points = 0
            for sent in doc.sents:
                if any(ent[1] >= sent.start_char and ent[2] <= sent.end_char for ent in entities):
                    points += 1
                    result.append("\n")
                    result.append(f"{points}. {sent.text.strip()}")
        else:
            result.append("\n")

        print("Ending Fetching PERCENT")
        result.append("\n")

        return ''.join(result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None


def CaseLawReferenced(FileText):
    try:
        print("Starting CaseLawReferenced function ")
        result = ["\n"]

        pattern = re.compile(r'\b[A-Z][a-zA-Z]* v\. [A-Z][a-zA-Z]*|\b[A-Z][a-zA-Z]* v\ [A-Z][a-zA-Z]*')
        doc = nlp(FileText)
        case_law_references = set(re.findall(pattern, FileText))

        for ent in doc.ents:
            if pattern.match(ent.text):
                case_law_references.add(ent.text)

        result.append("Case Law Reference : \n\n")
        for reference in case_law_references:
            result.append(f"{reference}")

        print("Ending CaseLawReferenced function")
        result.append("\n")

        return ''.join(result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def FetchLaws(FileText):
    print("Fetching Laws like CPC, PACE etc...")
    try:
        print("Now Fetching...")
        doc = nlp(FileText)
        result = ["Laws Refered : \n"]
        result.append("\n")


        entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ == "LAW"]

        points = 0
        printed_sentences = set()

        if entities:
            for entity in entities:
                start_char = entity[1]

                for sent in doc.sents:
                    if sent.start_char <= start_char < sent.end_char:
                        if sent.text not in printed_sentences:
                            points += 1
                            result.append(f"{points}. {sent.text}")
                            printed_sentences.add(sent.text)
                        break
        else:
            result.append("Laws Not Found")

        print("Ending Fetching Laws")
        result.append("\n")
        return ''.join(result).strip()
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None
    
def FetchIssues(FileText):
    try:
        print("Starting Issues")
        result = []

        result.append("\n")
        result.append("Issues : \n")
        pattern = r'issue\s*(.*?)(?:\.\s|\n|$)'
        match = re.search(pattern, FileText, re.DOTALL | re.IGNORECASE)
        if match:
            print("Issues Found")
            result.append('issue')
            result.append(match.group(1).strip())
            result.append("\n")
        result_text = ' '.join(result)
        result.append("\n")

        print("Ending Issues")
        return result_text
    except Exception as e:
        print(f"Exception occured : {e}")
        return None
    
def FetchConclusion(FileText):

    try:
        print("Starting Conclusion Function")

        paragraphs = re.split(r'\n\s*\n', FileText.strip())

        # Extract the last and second-to-last paragraphs
        last_paragraph = paragraphs[-1]
        second_last_paragraph = paragraphs[-2]

        # Print the paragraphs
        return ("Conclusion : \n" + second_last_paragraph + last_paragraph)
    
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None
    
def FetchLink(FileText):
    try:
        print("Fetching Article Link...")

        result = []
        result.append("\n\n")
        result.append("Link: ")

        # Updated regex to better match URLs
        url_regex = r'https?://[a-zA-Z0-9.-]+(?:/[^\s]*)?'

        links = re.findall(url_regex, FileText)

        # Filter valid links based on specific criteria
        valid_links = [link for link in links if link.endswith('.html') or link.endswith('.article')]

        if valid_links:
            result.append(" ".join(valid_links))
        else:
            result.append("No valid links found")

        result.append("\n")

        print("Ending Fetch Links")

        result_text = ''.join(result)
        return result_text

    except Exception as e:
        print(f"Exception occurred: {e}")
        return None

def main():

    #Path which contains LawGazette Articles
    directory = r"C:\Users\DELL\OneDrive\Desktop\LawGazette"

    #Path where you want to store summarised articles
    output_directory = r'C:\Users\DELL\OneDrive\Desktop\LawGazette\SummaryLawGazetteArticles'
    log_file_path = os.path.join(output_directory, 'processed_summarylg_files.log')

    os.makedirs(output_directory, exist_ok=True)

    processed_files = set()
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            processed_files = set(log_file.read().splitlines())

    files = OpenFiles(directory)

    for FileText, FileName in files:
        if FileName in processed_files:
            print(f"{FileName} has already been processed. Skipping...")
            continue

        output_content = []
        corrected_content = []

        output_content.extend(FetchCaseName(FileName))
        output_content.extend("\n")
        output_content.extend(FetchCourtName(FileText))
        #output_content.extend("\n")
        output_content.extend(QuestionsToTheCourt(FileText))
        output_content.extend("\n\n")
        output_content.extend(Summary(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchCosts(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchPercent(FileText))
        output_content.extend("\n")
        output_content.extend(CaseLawReferenced(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchLaws(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchIssues(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchConclusion(FileText))
        output_content.extend("\n\n")
        output_content.extend(FetchLink(FileText))

        corrected_content = Grammar(''.join(output_content))


        output_file_path = os.path.join(output_directory, f"processed_{FileName}")
        write_to_file(output_file_path, ''.join(corrected_content))

        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{FileName}\n")

if __name__ == "__main__":
    main()
