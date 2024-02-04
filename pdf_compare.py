import pandas as pd
import PyPDF2
from fuzzywuzzy import fuzz
import requests
from os.path import exists
import time
import json
from bs4 import BeautifulSoup
import pandas as pd 
import re
import os
import csv
import datetime

#bhddbcdjhujujhu

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'If-Modified-Since': 'Sun, 10 Dec 2023 00:38:34 GMT',
    'If-None-Match': '"139d3634c2bda27a04d6c9b1fc31f7be"',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

def download_pdf(url):
    save_path='./input/{0}.pdf'.format(url.split('/')[-1].replace(".pdf",""))
    file=exists(save_path)
    if(not file):
     
        response = requests.get(url,timeout=45)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"PDF downloaded successfully to: {save_path}")
        else:
            print(f"Failed to download PDF. Status code: {response.status_code}")

    return save_path

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
    return text

def compare_pdfs(pdf1_path, pdf2_path, threshold=90):
    text1 = extract_text_from_pdf(pdf1_path)
    text2 = extract_text_from_pdf(pdf2_path)

    similarity_ratio = fuzz.token_sort_ratio(text1, text2)

    if similarity_ratio >= threshold:
        output=[similarity_ratio,'yes']
    else:
        output=[similarity_ratio,'No']
    return output


def get_file_size(file_path):
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)  # Convert bytes to megabytes
        return size_mb
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
def extract_text_from_pdf_1(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        text = ""
        page_number =pdf_reader.numPages
        print(pdf_reader.numPages)
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
        out=[text,page_number]
    return out
def save_in_csv(wr, row_data):
    # Check if the CSV file already exists
    file_exists = os.path.isfile('./output/brochure_matching_pid_vs_docid.csv')

    with open('./output/brochure_matching_pid_vs_docid.csv', 'a', encoding='utf-8', errors='ignore', newline='') as file:
        writer = csv.writer(file, delimiter='|')

        # If the file doesn't exist, write the header row
        if not file_exists:
            writer.writerow(wr)

        # Construct a row based on the predefined header order and variable names
        row = [row_data.get(header, '') for header in wr]
        writer.writerow(row)

# Example usage:
wr=["product_id","docid","product_brochure_file_path","docid_brochure_file_path",'similarity_ratio','match','pdf1_status','pdf2_status','pdf1_text','pdf_1_text_extraction_status','pdf2_text','pdf_2_text_extraction_status','pdf1_size','pdf2_size','page_number_pdf2','page_number_pdf1']

df = pd.read_excel('/home/justdial/Downloads/brochure_matching_pid_vs_docid.xlsx')

for i in range(1,len(df)):
    row=df.iloc[i]
    pdf1=row['product_brochure_file_path']
    pdf2=row['docid_brochure_file_path']
    pdf1_path=download_pdf(pdf1)
    pdf2_path=download_pdf(pdf2)
    product_id=row['product_id']
    docid=row['docid']
    product_brochure_file_path=row['product_brochure_file_path']
    docid_brochure_file_path=row['docid_brochure_file_path']
    try:
        pdf1_size=get_file_size(pdf1_path)
    except:
        pdf1_size=""
        print("not able to get size")
    try:
        pdf2_size=get_file_size(pdf2_path)
    except:
        pdf2_size=""
        print("not able to get size")
    try:
        pdf1_status=extract_text_from_pdf_1(pdf1_path)
        pdf1_text=pdf1_status[0]
        page_number_pdf1=pdf1_status[1]
        pdf_1_text_extraction_status="data found "
        if not pdf1_text.strip():
            print("text_extracting= 'have only blank text'")
            pdf_1_text_extraction_status="No data found "
        pdf1_status="readable"
    except:
        pdf1_text=""
        pdf_1_text_extraction_status=""
        page_number_pdf1=""
        pdf1_status="not readable"
        
    try:
        pdf2_status=extract_text_from_pdf_1(pdf2_path)
        pdf2_text=pdf2_status[0]
        page_number_pdf2=pdf2_status[1]
        pdf_2_text_extraction_status="data found "
        if not pdf2_text.strip():
            print("text_extracting= 'have only blank text'")
            pdf_2_text_extraction_status="No data found "
        pdf2_status="readable"
    except:
        page_number_pdf2=""
        pdf2_text=""
        pdf_2_text_extraction_status=""
        pdf2_status="not readable"
       
    try:
        output=compare_pdfs(pdf1_path, pdf2_path)
        print(output)
        similarity_ratio=output[0]
        match=output[1]
        row_data={'product_id':product_id,'docid':docid,'product_brochure_file_path':product_brochure_file_path,'docid_brochure_file_path':docid_brochure_file_path,'similarity_ratio':similarity_ratio,'match':match,'pdf1_status':pdf1_status,'pdf2_status':pdf2_status,'pdf1_text':pdf1_text,'pdf_1_text_extraction_status':pdf_1_text_extraction_status,'pdf2_text':pdf2_text,'pdf_2_text_extraction_status':pdf_2_text_extraction_status,'pdf1_size':pdf1_size,'pdf2_size':pdf2_size,'page_number_pdf2':page_number_pdf2,'page_number_pdf1':page_number_pdf1}
        save_in_csv(wr,row_data)
    except:
        row_data={'product_id':product_id,'docid':docid,'product_brochure_file_path':product_brochure_file_path,'docid_brochure_file_path':docid_brochure_file_path,'similarity_ratio':"",'match':"",'pdf1_status':pdf1_status,'pdf2_status':pdf2_status,'pdf1_text':pdf1_text,'pdf_1_text_extraction_status':pdf_1_text_extraction_status,'pdf2_text':pdf2_text,'pdf_2_text_extraction_status':pdf_2_text_extraction_status,'pdf1_size':pdf1_size,'pdf2_size':pdf2_size,'page_number_pdf2':page_number_pdf2,'page_number_pdf1':page_number_pdf1}
        save_in_csv(wr,row_data)
         
    
