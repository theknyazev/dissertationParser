import pandas as pd
import requests
import fitz

file_path = 'database.csv'
df = pd.read_csv(file_path)

df['PDF_Text'] = ''
df['Научный руководитель'] = ''
df['Официальные оппоненты'] = ''
df['Ведущая организация'] = ''

def extract_text_from_pdf(pdf_url):
    response = requests.get(pdf_url)
    pdf_path = "temporary.pdf"

    with open(pdf_path, "wb") as file:
        file.write(response.content)

    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text("text") + "\n"

    return text


def parse_diss_text(text):
    lines = text.split('\n')
    info = {
        "Научный руководитель": "",
        "Официальные оппоненты": "",
        "Ведущая организация": ""
    }

    ind1 = text.find('Научный руководитель')
    if ind1 < 0:
        ind1 = text.find('Научный консультант')
    ind2 = text.find('Официальные оппоненты')
    ind3 = text.find('Ведущая организация')
    ind4 = text[ind3:].find('Защита') + ind3

    info = {
        "Научный руководитель": text[ind1:ind2],
        "Официальные оппоненты": text[ind2:ind3],
        "Ведущая организация": text[ind3:ind4]
    }

    return info


count = 0
threshold = 100000

for index, row in df.iloc[count:].iterrows():
    count += 1
    print(count)
    if count >= threshold:
        break
    pdf_url = row['PDF Link']
    try:
        pdf_text = extract_text_from_pdf(pdf_url).replace('\n', ' ').replace('   ', ' ').replace('  ', ' ').replace('''
    ''', ' ')
        parsed_info = parse_diss_text(pdf_text)

        df.at[index, 'PDF_Text'] = pdf_text
        df.at[index, 'Научный руководитель'] = parsed_info['Научный руководитель'].strip().replace(' – ', ' ').replace(': ', ' ')
        df.at[index, 'Официальные оппоненты'] = parsed_info['Официальные оппоненты'].strip().replace(' – ', ' ').replace(': ', ' ')

        df.at[index, 'Ведущая организация'] = parsed_info['Ведущая организация'].strip().replace(' – ', ' ').replace(': ', ' ')
    except Exception as e:
        print(f"ERROR at {pdf_url} with message {e}")

output_file_path = 'result.csv'
df.to_csv(output_file_path, index=False)

print("Completed")
