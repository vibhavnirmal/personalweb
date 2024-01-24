from transformers import pipeline, NougatProcessor, VisionEncoderDecoderModel
from collections import Counter
from pdf2image import convert_from_path

class KeyWordExtractor:
    def __init__(self, device="cuda", num_workers=1):
        self.num_workers = num_workers  # Number of workers for the pipeline
        self.pipe = pipeline("text2text-generation", model="ilsilfverskiold/tech-keywords-extractor", device=device)

    def extract_keywords(self, document):
        notes = document.split("\n")  # Split into sentences
        # if sentence is > 100 characters, split into smaller sentences
        notes = [note[i:i+100] for note in notes for i in range(0, len(note), 100)]
        notes = [note.strip() for note in notes if note.strip()]  # Remove extra whitespace

        all_keywords = Counter()  # Use Counter for keyword accumulation and frequency

        for sentence in notes:
            try:
                generated_keywords = self.pipe(sentence, max_length=100, do_sample=True, top_k=50, top_p=0.95, num_workers=self.num_workers)[0]["generated_text"]
                all_keywords.update(keyword.strip() for keyword in generated_keywords.split(","))
            except Exception as e:
                print(f"Error processing sentence: {sentence}")
                print(f"Error details: {e}")

        return list(all_keywords.keys())  # Return a list of keywords
        
class PDFExtractor:
    def __init__(self, device="cuda", num_workers=1):
        self.num_workers = num_workers
        self.processor = NougatProcessor.from_pretrained("facebook/nougat-base")
        self.model = VisionEncoderDecoderModel.from_pretrained("facebook/nougat-base")
        self.model.to(device)

    def extract_text(self, filepath):
        images = convert_from_path(filepath)

        pixel_values = self.processor(images, return_tensors="pt").pixel_values

        # generate transcription (here we only generate 30 tokens)
        outputs = self.model.generate(
            pixel_values.to(device),
            min_length=1,
            max_new_tokens=3000,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
        )

        sequence = self.processor.batch_decode(outputs, skip_special_tokens=True)[0]
        sequence = self.processor.post_process_generation(sequence, fix_markdown=False)

        # remove (\backslash) from the sequence
        sequence = sequence.replace("\\backslash", "")
        sequence = sequence.replace("\(\)", "")
        sequence = sequence.replace("###### Abstract", "")

        return sequence


if __name__ == "__main__":
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"

    def kw_extract_test():
        # test Keyword Extractor
        DOCUMENT = """
        What You'll Need To Succeed
        Pursuing a degree in Computer Engineering, Computer Science, Electrical Engineering, Robotics or a related field. Must be enrolled in a full time degree program at the time of the internship and for the semester following the internship (Fall 2022)
        Experience building simulations for industry or research
        Excellent C++ or Python programming and software design skills
        Strong mathematical skills, including linear algebra, numerical methods, and stochastic methods
        Passion for solving challenging, impactful problems
        Nice To Haves
        Students pursuing MS/PhD in computer science, computer vision, machine learning or robotics and with a strong interest in applying their skills to write software to solve challenging problems
        Expertise in large-scale cloud infrastructure, GCP/AWS/Azure
        Experience in ML systems (data selection, feature extraction, training, verification, analysis and infra) 
        Familiarity with PyTorch, Keras, Tensorflow, Caffe or other similar deep net or machine learning package
        """

        extractor = KeyWordExtractor(device=device, num_workers=8)
        extracted_keywords = extractor.extract_keywords(DOCUMENT)
        print(extracted_keywords)

    def pdf_extract_test():
        # test PDF Extractor
        resume_file_path ="E:\\coding\\github_pulls\\personalweb\\ignore\\resume_vibhav.pdf"

        pdf_extractor = PDFExtractor(device=device, num_workers=8)
        extracted_text = pdf_extractor.extract_text(resume_file_path)
        print(extracted_text)

    
    kw_extract_test()





    
    