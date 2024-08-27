import os
import nltk
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, AutoModelForSeq2SeqLM , PegasusTokenizer, PegasusForConditionalGeneration, pipeline
import pandas as pd
import re
import language_tool_python

#nlp = spacy.load('en_core_web_sm')
nlp = spacy.load("en_core_web_md")
nltk.download('punkt')
pd.set_option("display.max_rows", 200)

MAX_SEGMENTS = 1000  # Set a reasonable maximum number of segments to process per file

def OpenFiles(directory):
    #storing the name of files in array
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                #print(f"Opened File {filename}")
                files.append((text, filename))
    return files

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

#writing the content into the file
def write_to_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

#function to fetch the Name of the case
def FetchCaseName(FileName):
    print(f"Processing {FileName}")
    return f"Name of the Case is : {FileName}\n\n"

def FetchCourtName(file_text):
    print("FetchCourtName Function Started...")

    result = []
    result.append("\n")

    # Tokenize text into words
    doc = nlp(file_text)
    words = [token.text for token in doc]

    # Retrieve the first 1024 words
    first_1024_words = ' '.join(words[:1024])
    
    # Optionally, use the chunk splitter to work with this text
    custom_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
    )
    texts = custom_text_splitter.create_documents([first_1024_words])

    if len(texts) < 2:
        result.append("Insufficient text chunks to process.")
        return result
    
    contents = texts[0].page_content

    if('EWHC' in contents):
        print("Found EWHC court names")
        result.append("Court Name : ENGLAND & WALES HIGH COURT ")

    elif('EWCA' in contents):
        print("Found EWCA")
        result.append("Court Name : ENGLAND & WALES COURT OF APPEAL")

    if('KB' in contents):
        print("FOUND KB")
        result.append("KING'S BENCH DIVISION")
        result.append("\n")
    
    if('CH' in contents or 'ch' in contents):
        print("FOUND CH")
        result.append("CHANCERY DIVISION")
        result.append("\n")
    
    if('SCCO' in contents or 'SCC' in contents):
        print("FOUND SCCO")
        result.append("SENIOUR COURT COSTS OFFICE")
        result.append("\n")

    if('QB' in contents or 'qb' in contents):
        print("FOUND QB")
        result.append("QUEEN'S BENCH DIVISION")
        result.append("\n")

    print("Ending FetchCourtName Function")
    return result

#function to fetch the Court Name where the case is heared
def FetchJudgeName(file_text):
    print("FetchJudgeName Function Started...")

    result = []
    result.append("\n")
    result.append("Justice : ")

    # Tokenize text into words
    doc = nlp(file_text)
    words = [token.text for token in doc]

    # Retrieve the first 1024 words
    first_1024_words = ' '.join(words[:1024])
    
    # Optionally, use the chunk splitter to work with this text
    custom_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=20,
        length_function=len,
    )
    texts = custom_text_splitter.create_documents([first_1024_words])
    
    if len(texts) < 2:
        result.append("Insufficient text chunks to process.")
        return result
    
    # Iterate over all chunks and check for relevant information
    content = texts[0].page_content

    # Check for relevant terms indicating court name or judge
    if ('Justice' in content):
        print('Justice Exist')
        start_index = content.index("Justice") + len("Justice")
        next_string = content[start_index:].split()[0] 
        result.append(next_string)
        result.append("\n")
        #print(next_string)
        
    elif('Judge' in content):
        print('Judge Exist')
        start_index = content.index("Judge") + len("Judge")
        next_string = content[start_index:].split()[0]  
        result.append(next_string)
        result.append("\n")
        #print(next_string)

    elif('judgment of' in content):
        print("Judgment Exist")
        start_index = content.index("judgment of") + len("judgment of")
        next_string = content[start_index:].split()[0]  
        result.append(next_string)
        result.append("\n")
        #print(next_string)  
    
    elif('decision of' in content):
        print('Decision Exist') 
        start_index = content.index("decision of") + len("decision of")
        next_string = content[start_index:].split()[0]  
        result.append(next_string)
        result.append("\n")       

    elif('Sir' in content):
        print('Sir Exist') 
        start_index = content.index("Sir") + len("Sir")
        next_string = content[start_index:].split()[0]  
        result.append(next_string)
        result.append("\n")   

    elif('Costs Judge' in content):
        print('Costs Judge') 
        start_index = content.index("Costs Judge") + len("Costs Judge")
        next_string = content[start_index:].split()[0]  
        result.append(next_string)
        result.append("\n")

    else:
        print("Not Exist")
        result.append("Court name or judge information not found.")
        result.append("\n")

    print("Ending FetchCourtName Function")
    return result

def FetchIssueToBeConsidered(FileText):

    try:
        print("Starting Issue to Be Consiered")
        result = []

        result.append("\n")
        result.append("Issue to be Considered : \n")
        pattern = r'issue\s*(.*?)(?:\.\s|\n|$)'
        match = re.search(pattern, FileText, re.DOTALL | re.IGNORECASE)
        if match:
            print("Issues Found")
            result.append('issue')
            result.append(match.group(1).strip())
            result.append("\n")
        result_text = ' '.join(result)
        result.append("\n")

        print("Ending Issue to Be Considered")
        return result_text
    except Exception as e:
        print(f"Exception occured : {e}")
        return None

def QuestionsForTheCourt(FileText):

    try:

        print("Fetching Questions for the Court")
        result = []
        result.append("\n") 
        result.append("Questions For The Court : \n")

        pattern = r'Whether\s* (.*?)(?:\.\s|\n|$)'
        matches = re.finditer(pattern, FileText, re.DOTALL | re.IGNORECASE)

        question_number = 1
        for match in matches:
            question = match.group(1).strip()
            if question:
                result.append(f"{question_number}. Whether {question}")
                question_number += 1
                result.append("\n") 

        result.append("\n") 
        result_text = ''.join(result) 
        print("Ending Fetching questions to the Court")
        return result_text
    except Exception as e:
        print(f"Exception occured : {e}")
        return None

#Function to Fetch Claimant's Position from the text file
def ClaimantPosition(FileText):
    print("Starting ClaimantPosition function")

    #This array stores only heading String " " 
    result1 = ["Appellant Argues in the Court:\n\n"]

    #This array stores the summarised Appelant points 
    result = []
    doc = nlp(FileText)

    #Using NLP and filter searching to find Appelant word or entity occured in the File
    #entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ("Appellant" in ent.text or "solicitors" in ent.text or "Claimant" in ent.text or "Claimants" in ent.text or "Claimant's" in ent.text or "Client" in ent.text) and ent.label_ in {"ORG", "PERSON"}]

    #keywords = ("claimant", "solicitors", "appellant", "claimants", "claimant's", "client")
    #entities = [
    #(ent.text, ent.start_char, ent.end_char, ent.label_)
    #for ent in doc.ents
    #if any(keyword in ent.text.lower() for keyword in keywords) and ent.label_ in {"ORG", "PERSON"}
#]

    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if "Apellant" or "Claimant" in ent.text and ent.label_ in {"ORG", "PERSON"}]

    #Getting total length of the texts
    text_length = len(FileText)

    #Start positon of Appelant word 
    start_pos = 0

    #1 segment = 1440 words and segment count is made explictly limited to 10 that is 14,440 words only.
    segment_count = 0

    pegasus_tokenizer = PegasusTokenizer.from_pretrained('google/pegasus-large')
    pegasus_model = PegasusForConditionalGeneration.from_pretrained('google/pegasus-large')

    while start_pos < text_length:
        #If Appelant word is not found then finding summary of appelant through different approch
        if segment_count >= MAX_SEGMENTS:
            print(f"Reached maximum segment limit ({MAX_SEGMENTS}). Stopping further processing for this file.")
            
            print("Starting Another Approch to find Applicant Points")

            result = []
            #using roberta Q&A model
            model_name = "deepset/roberta-base-squad2"
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)

            qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

            questions = {
                "Applicant's Position : ": "What did the appellant argue?",
            }
            results = {}

            for key, question in questions.items():
                try:
                    answer = qa_pipeline(question=question, context=FileText)
                    results[key] = answer['answer']
                except Exception as e:
                    results[key] = str(e)

            for key, result_text in results.items():
                result.append(f"{key}\n{result_text}\n\n")

            print("Ending Applicant Postion function")
            return result

        #If Appelant word is not found in text then find in another chunk of text
        text_segment = FileText[start_pos:start_pos + 1440]
        NERtexts = entities

        #If word found
        if NERtexts:
            for reference in NERtexts:
                #then summarzing that specific chunk
                tokenizer = AutoTokenizer.from_pretrained('t5-base')
                model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')

                #ref1 is position start of character and ref2 is end position of character
                entity_text = text_segment[reference[1]:reference[2]]
                next_chars_start = start_pos + reference[2]
                next_chars_end = min(next_chars_start + 1440, text_length)
                next_chars = FileText[next_chars_start:next_chars_end]

                input_text = "summarize: " + next_chars
                input_ids = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)

                output = model.generate(input_ids, min_length=80, max_length=100)

                summary = tokenizer.decode(output[0], skip_special_tokens=True)
                
                sentences = nltk.sent_tokenize(summary)

                #Avoding the sentences get doubled
                seen_sentences = set()
                unique_sentences = []

                for sentence in sentences:
                    if sentence not in seen_sentences:
                        unique_sentences.append(sentence)
                        seen_sentences.add(sentence)

                unique_summary = ' '.join(unique_sentences)
                result.append(f"{unique_summary}\n")

                start_pos = next_chars_end
                break
            else:
                start_pos += 1440
        segment_count += 1
        if segment_count % 10 == 0:
            print(f"Processed {segment_count} segments")
    #storing and adding results
    result.append("\n")

    #Getting the total length of our summary
    lengthsummary = sum(len(segment) for segment in result)
    lengthsummary_str = str(lengthsummary)

    #If the length of our summary is more than 2048 characters then summarizing it again using T5 model
    if lengthsummary > 2048:
        print("Summary more than 2048 so starting t5")
        model_name = 'T5-base'
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            inputs = tokenizer.encode("Summarized : "+" ".join(result), return_tensors='pt', max_length=1024, truncation=True)
            output = model.generate(inputs, min_length=80, max_length=512)
            new_summary = tokenizer.decode(output[0], skip_special_tokens=True)

            print("Ending Appelant's t5")

            print("Now using Pegasus")
            inputid = pegasus_tokenizer.encode(new_summary, return_tensors='pt', max_length=1024, truncation=True)
            summaryid = pegasus_model.generate(inputid, num_beams=9, no_repeat_ngram_size=3, length_penalty=2.0, min_length=80, max_length=200, early_stopping=True)
            processsummary = pegasus_tokenizer.decode(summaryid[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
            print("Ending Pegasus Applicant Function")
            return result1 + [processsummary]

        except Exception as e:
            print(f"Error loading model or tokenizer: {e}")

    else:
        print("Ending ClaimantPosition function")
        return result1 + result

def DefendantPosition(FileText):
    print("Starting DefendantPosition function")
    result1 = ["\n Defendant Argues in the Court:\n\n"]

    #Storing Summary in below array
    result = []
    result.append("\n\n")
    
    #Using NLP and filter searching to find Appelant word or entity occured in the File
    doc = nlp(FileText)
    #entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ("Defendant" in ent.text or "Respondent" in ent.text or "defedant's" in ent.text or "defedant" in ent.text) and ent.label_ in {"ORG", "PERSON"}]

    #keywords = ("defendant", "respondent", "defendant's")
    #entities = [
    #(ent.text, ent.start_char, ent.end_char, ent.label_)
    #for ent in doc.ents
    #if any(keyword in ent.text.lower() for keyword in keywords) and ent.label_ in {"ORG", "PERSON"}
#]
    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if "Defendant" or "Respondent" in ent.text and ent.label_ in {"ORG", "PERSON"}]

    #Fetching the total length of the text
    text_length = len(FileText)
    start_pos = 0

    #Each segment is of 1024 characters
    segment_count = 0

    pegasus_tokenizer = PegasusTokenizer.from_pretrained('google/pegasus-large')
    pegasus_model = PegasusForConditionalGeneration.from_pretrained('google/pegasus-large')

    while start_pos < text_length:
        if segment_count >= MAX_SEGMENTS:
            print(f"Reached maximum segment limit ({MAX_SEGMENTS}). Stopping further processing for this file.")
            
            print("Starting Backup Approch to find Defedant Points")
            result = []
            model_name = "deepset/roberta-base-squad2"
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)
            questions = {
                "Defendant's Position : ": "What did Defedant argue?",
            }
            results = {}
            for key, question in questions.items():
                try:
                    answer = qa_pipeline(question=question, context=FileText)
                    results[key] = answer['answer']
                except Exception as e:
                    results[key] = str(e)
            for key, result_text in results.items():
                result.append(f"{key}\n{result_text}\n\n")
            print("Ending Defedant Postion function")
            return result

        text_segment = FileText[start_pos:start_pos + 1024]
        NERtexts = entities

        if NERtexts:
            for reference in NERtexts:
                tokenizer = AutoTokenizer.from_pretrained('t5-base')
                model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
                entity_text = text_segment[reference[1]:reference[2]]
                next_chars_start = start_pos + reference[2]
                next_chars_end = min(next_chars_start + 1024, text_length)
                next_chars = FileText[next_chars_start:next_chars_end]

                input_text = "summarize: " + next_chars
                input_ids = tokenizer.encode(input_text, return_tensors='pt', max_length=512, truncation=True)
            
                output = model.generate(input_ids, min_length=80, max_length=100)
            
                summary = tokenizer.decode(output[0], skip_special_tokens=True)
                sentences = nltk.sent_tokenize(summary)
                seen_sentences = set()
                unique_sentences = []

                #Avoiding double sentence in the summary
                for sentence in sentences:
                    if sentence not in seen_sentences:
                        unique_sentences.append(sentence)
                        seen_sentences.add(sentence)
                
                #Joining unique summaries to each previous summary
                unique_summary = ' '.join(unique_sentences)
                result.append(f"{unique_summary}\n")
                
                start_pos = next_chars_end
                break
            else:
                result.append("No relevant entities found in this segment.\n")
                start_pos += 1024
        segment_count += 1
        if segment_count % 10 == 0:
            print(f"Processed {segment_count} segments")

    result.append("\n")

    lengthsummary = sum(len(segment) for segment in result)
    lengthsummary_str = str(lengthsummary)

    if lengthsummary > 2048:
        print("Summary more than 2048 so starting t5")
        model_name = 'T5-base'
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            inputs = tokenizer.encode("Summarized : "+" ".join(result), return_tensors='pt', max_length=1024, truncation=True)
            output = model.generate(inputs, min_length=80, max_length=512)
            new_summary = tokenizer.decode(output[0], skip_special_tokens=True)
            print("Ending Defedant Position function t5")

            print("Now using Pegasus")
            inputid = pegasus_tokenizer.encode(new_summary, return_tensors='pt', max_length=1024, truncation=True)
            summaryid = pegasus_model.generate(inputid, num_beams=9, no_repeat_ngram_size=3, length_penalty=2.0, min_length=80, max_length=200, early_stopping=True)
            processsummary = pegasus_tokenizer.decode(summaryid[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
            print("Ending Pegasus Defendant Function")
            return result1 + [processsummary]   
            
        except Exception as e:
            print(f"Error loading model or tokenizer: {e}")

    else:

        print("Ending Defedant Position function")
        return result1 + result

#Fetching Case Law Referenced in the entire article
def CaseLawReferenced(FileText):
    print("Starting CaseLawReferenced function")
    result = []
    #using Regular expression to find words like v. and v and fetcing the previous and next character from v 
    pattern = re.compile(r'\b[A-Z][a-zA-Z]* v\. [A-Z][a-zA-Z]*|\b[A-Z][a-zA-Z]* v\ [A-Z][a-zA-Z]*')

    doc = nlp(FileText)
    result.append("\n")
    case_law_references = set(re.findall(pattern, FileText))

    for ent in doc.ents:
        if pattern.match(ent.text):
            case_law_references.add(ent.text)

    result.append("Case Law Reference:\n\n")
    for reference in case_law_references:
        result.append(f"{reference}\n")
    result.append("\n")
    print("Ending CaseLawReferenced function")
    return result

def FetchLaws(FileText):

    print("Fetching Laws like IPC, CRPC, CPC Started")
    try:
        print("Now Fetching...")
        doc = nlp(FileText)

        result = []

        result.append("Laws Refered : \n")

        entites = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in {"LAW"}]

        points = 0
        printed_sentences = set()

        if entites:
            for entity in entites:
                start_char = entity[1]

                for sent in doc.sents:
                    if sent.start_char <= start_char < sent.end_char:
                        if sent.text not in printed_sentences:
                            points +=1
                            result.append("\n")
                            result.append(f"{points}. {sent.text}")
                            printed_sentences.add(sent.text)
                        break
        else:
            result.append("Laws Not Found \n")

        result.append("\n")
        result_text = ' '.join(result)
        print("Ending Fetching Laws")
        return result_text
    except Exception as e:
        print(f"Exception occured : {e}")
        return None


def IssuesConsideredAndOutcome(FileText):
    print("Starting IssuesConsideredAndOutcome function")
    result = []
    #using roberta Q&A model
    model_name = "deepset/roberta-base-squad2"
    model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    qa_pipeline = pipeline("question-answering", model=model, tokenizer=tokenizer)

    questions = {
        "Issues considered by the Judge : ": "What are Issues considered by the Judge in the entire summary?",
        "Outcome : ": "What was the outcome?"
    }
    results = {}

    for key, question in questions.items():
        try:
            answer = qa_pipeline(question=question, context=FileText)
            results[key] = answer['answer']
        except Exception as e:
            results[key] = str(e)

    for key, result_text in results.items():
        result.append(f"{key}\n{result_text}\n\n")

    print("Ending IssuesConsideredAndOutcome function")
    return result

def Conclusion(FileText):
    print("Conclusion Function started : ")

    result = []

    pattern = r'Conclusion\s*(.*?)(?:\n = \0|\Z)'

    match = re.search(pattern, FileText, re.DOTALL| re.IGNORECASE)

    result.append('Conclusion : ')

    if match:
        result.append (match.group(1).strip())  # Return the matched string
        print("Conclusion Found")
        #print(result)

    elif match:
        pattern = r'Summary\s*(.*?)(?:\n = \0|\Z)'

        match = re.search(pattern, FileText, re.DOTALL| re.IGNORECASE)
        result.append (match.group(1).strip())
        print ("Summary found")

    return result

def FetchCosts(FileText):

    print("Fetching Costs Started")
    try:
        print("Now Fetching...")
        doc = nlp(FileText)

        result = []

        result.append("Costs : \n")

        entites = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ent.label_ in {"MONEY"}]

        points = 0
        printed_sentences = set()

        if entites:
            for entity in entites:
                start_char = entity[1]

                for sent in doc.sents:
                    if sent.start_char <= start_char < sent.end_char:
                        if sent.text not in printed_sentences:
                            points +=1
                            result.append("\n")
                            result.append(f"{points}. {sent.text}")
                            printed_sentences.add(sent.text)
                        break
        else:
            result.append("Costs Not Found \n")

        result.append("\n")
        result_text = ' '.join(result)
        print("Ending Fetching Costs")
        return result_text
    except Exception as e:
        print(f"Exception occured : {e}")
        return None

def FetchLinks(FileText):

    try:
        print("Starting to Fetch Links")

        result = []
        result.append("\n")
        result.append("\nLink : ")

        url_regex = r"https?://[a-zA-Z0-9.-]+(?:/[^\s]*)?"

        links = re.findall(url_regex, FileText)

        valid_links = [link for link in links if link.endswith('.html') and not link.endswith('Cite')]

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

def Ner_Case_Claimant(text):
    result = []
    content = text

    doc = nlp(content)

    # Filter for "Claimant" or "Appellant"
    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ("Apellant" in ent.text or "solicitors" in ent.text or "Claimant" in ent.text or "Claimants" in ent.text or "Claimant's" in ent.text or "Client" in ent.text) and ent.label_ in {"ORG", "PERSON"}]
    
    #keywords = ("claimant", "solicitors", "appellant", "claimants", "claimant's", "client")
    #entities = [
    #(ent.text, ent.start_char, ent.end_char, ent.label_)
    #for ent in doc.ents
    #if any(keyword in ent.text.lower() for keyword in keywords) and ent.label_ in {"ORG", "PERSON"}
#]

    #entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if "Apellant" or "Claimant" in ent.text and ent.label_ in {"ORG", "PERSON"}]

    printed_sentences = set()

    if entities:
        for entity in entities:
            start_char = entity[1]

            for sent in doc.sents:
                if sent.start_char <= start_char < sent.end_char:
                    if sent.text not in printed_sentences:
                        result.append(f"{sent.text}\n")
                        printed_sentences.add(sent.text)
                    break
    else:
        #result.append("Claimant not found\n")
        result.append("\n")

    return ''.join(result)

def Ner_Case_Defendant(text):
    result = []
    content = text

    doc = nlp(content)

    # Filter for "Defendant" or "Respondent"
    entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if ("Defendant" in ent.text or "Respondent" in ent.text or "defedant's" in ent.text or "defedant" in ent.text) and ent.label_ in {"ORG", "PERSON"}]
    
    #keywords = ("defendant", "respondent", "defendant's")
    #entities = [
    #(ent.text, ent.start_char, ent.end_char, ent.label_)
    #for ent in doc.ents
    #if any(keyword in ent.text.lower() for keyword in keywords) and ent.label_ in {"ORG", "PERSON"}
#]

    #entities = [(ent.text, ent.start_char, ent.end_char, ent.label_) for ent in doc.ents if "Defendant" or "Respondent" in ent.text and ent.label_ in {"ORG", "PERSON"}]

    printed_sentences = set()

    if entities:
        for entity in entities:
            start_char = entity[1]

            for sent in doc.sents:
                if sent.start_char <= start_char < sent.end_char:
                    if sent.text not in printed_sentences:
                        result.append(f"{sent.text}\n")
                        printed_sentences.add(sent.text)
                    break
    else:
        #result.append("Defendant not found\n")
        result.append("\n")

    return ''.join(result)

def ClaimantAnalysis(text):
    doc = nlp(text)
    reference_sentence = "Claimant argues in the court"
    ref_doc = nlp(reference_sentence)

    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # Calculate similarities between sentences and reference sentence
    similarities = []

    for sent in sentences:
        # Compare with the reference sentence
        ref_sim = ref_doc.similarity(nlp(sent))
        similarities.append((ref_sim, reference_sentence, sent))

    # Sort similarities by score in descending order
    similarities.sort(reverse=True, key=lambda x: x[0])

    # Collect the top 2 pairs without repeating sentences
    top_sentences = []
    used_sentences = set()

    for sim, ref_sent, sent in similarities:
        if len(top_sentences) >= 3:
            break
        if sent not in used_sentences:
            top_sentences.append((sim, ref_sent, sent))
            used_sentences.add(sent)

    result = []
    points = 1
    for sim, ref_sent, sent in top_sentences:
        result.append("\n")
        #result.append(f"{points}. Reference: {ref_sent} \nSentence: {sent} \nSimilarity Score: {sim:.2f}")
        result.append(f"{points}. {sent} \n")
        points += 1
    
    return result

def DefendantAnalysis(text):
    doc = nlp(text)

    reference_sentence = "Defendant argues in the court"

    ref_doc = nlp(reference_sentence)

    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # Calculate similarities between sentences and reference sentence
    similarities = []

    for sent in sentences:
        # Compare with the reference sentence
        ref_sim = ref_doc.similarity(nlp(sent))
        similarities.append((ref_sim, reference_sentence, sent))

    # Sort similarities by score in descending order
    similarities.sort(reverse=True, key=lambda x: x[0])

    # Collect the top 2 pairs without repeating sentences
    top_sentences = []
    used_sentences = set()

    for sim, ref_sent, sent in similarities:
        if len(top_sentences) >= 3:
            break
        if sent not in used_sentences:
            top_sentences.append((sim, ref_sent, sent))
            used_sentences.add(sent)

    result = []
    points = 1
    for sim, ref_sent, sent in top_sentences:
        #result.append(f"{points}. Reference: {ref_sent} \nSentence: {sent} \nSimilarity Score: {sim:.2f}")
        result.append("\n")
        result.append(f"{points}. {sent} \n")
        points +=1
    
    return result

def main():
    directory = r"C:\Users\DELL\OneDrive\Desktop\NEW1\CivilLitigationBriefArticles"
    output_directory = r"C:\Users\DELL\OneDrive\Desktop\NEW1\CivilLitigationBriefArticles\summaryclboutput"
    log_file_path = os.path.join(output_directory, 'processed_clb_summary.log')

    os.makedirs(output_directory, exist_ok=True)

    #Maintaing a log file to keep track of processed files so processed files dont get summarized twice
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
        output_content.extend(FetchCourtName(FileText))
        output_content.extend(FetchJudgeName(FileText))
        output_content.extend(FetchIssueToBeConsidered(FileText))
        output_content.extend(QuestionsForTheCourt(FileText))
        output_content.extend(ClaimantPosition(FileText))

        claimant_summary = Ner_Case_Claimant(FileText)
        output_content.extend("\n")
        output_content.extend(ClaimantAnalysis(claimant_summary))
        output_content.extend("\n")

        output_content.extend(DefendantPosition(FileText))

        defedant_summary = Ner_Case_Defendant(FileText)
        output_content.extend("\n")
        output_content.extend(DefendantAnalysis(defedant_summary))
        output_content.extend("\n")

        output_content.extend(CaseLawReferenced(FileText))
        output_content.extend("\n")

        output_content.extend(FetchLaws(FileText))
        output_content.extend(IssuesConsideredAndOutcome(FileText))
        output_content.extend("\n")
        output_content.extend(Conclusion(FileText))
        output_content.extend("\n")
        output_content.extend(FetchCosts(FileText))
        output_content.extend("\n")
        output_content.extend(FetchLinks(FileText))

        corrected_content = Grammar(''.join(output_content))

        output_file_path = os.path.join(output_directory, f"processed_{FileName}")
        write_to_file(output_file_path, ''.join(corrected_content))

        with open(log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{FileName}\n")

if __name__ == "__main__":
    main()
