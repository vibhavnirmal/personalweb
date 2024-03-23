from .extensions import db
from .models.companies import Company
from .models.keywords import Keyword, KeywordAssociation

try:
    from ollama import generate
    ollama_available = True
except:
    print("Ollama not installed")
    ollama_available = False


def get_all_company_names():
    column_values = list(db.session.query(Company.company_name).all())
    names = [value[0] for value in column_values]
    return names

def get_company_id(name):
    company = Company.query.filter_by(company_name=name).first()
    if company:
        return company.id
    else:
        company = Company(company_name=name)
        db.session.add(company)
        db.session.commit()
        return company.id

def preprocess_data(text):
    text = ''.join(map(lambda x: x.lower(), text))
    text = text.replace("\n", " ")
    # remove leading/trailing whitespace
    text = text.strip()
    
    return text

def generate_keywords(notes):
    my_prompt = "[INST] Generate comma separated keywords from the given job description. Keywords should not contain more than 3 words. \n\n" + notes + "\n\n [/INST]"

    if len(notes) < 50:
        return []

    if ollama_available:
        response = generate('mistral', my_prompt)
        keywords = response['response']

        # Use set comprehension for keyword preprocessing
        setOfKeywords = {preprocess_data(kw) for kw in keywords.split(",")}
        
        return setOfKeywords
    else:
        return []

def insert_keywords(application_id, desc):
    if ollama_available:
        keywords_from_notes = generate_keywords(desc)
        print(keywords_from_notes)

        if keywords_from_notes:
            for keyword in keywords_from_notes:
                keyword_exists = Keyword.query.filter_by(keyword=keyword).first()
                if keyword_exists:
                    keyword_exists.frequency += 1
                else:
                    new_keyword = Keyword(keyword=keyword, frequency=1)
                    db.session.add(new_keyword)
                    db.session.flush()

                    new_keyword_association = KeywordAssociation(keyword_id=new_keyword.id, application_id=application_id)
                    db.session.add(new_keyword_association)

            db.session.commit()
        else:
            print("No keywords generated")
    else:
        print("Ollama not installed")