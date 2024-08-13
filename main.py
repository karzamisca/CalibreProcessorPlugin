import re
import os
import zipfile
from bs4 import BeautifulSoup
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.pdf_text_extractor.ui import PDFTextExtractorDialog
from PyQt5.QtWidgets import QMessageBox

class PDFTextExtractorInterface(InterfaceAction):
    name = 'PDF Text Extractor'

    action_spec = ('PDF Text Extractor', None, 'Extract text from PDF and EPUB files', 'Ctrl+Shift+E')

    def genesis(self):
        icon = get_icons('images/icon.png', 'PDF Text Extractor')
        self.qaction.setIcon(icon)
        self.qaction.triggered.connect(self.show_dialog)

    def show_dialog(self):
        base_plugin_object = self.interface_action_base_plugin
        do_user_config = base_plugin_object.do_user_config
        d = PDFTextExtractorDialog(self.gui, self.qaction.icon(), do_user_config)
        d.show()

    def split_sentences(self, text):
        sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
        return sentence_endings.split(text)

    def clean_text(self, text):
        cleaned_text = re.sub(r'\n+', '\n', text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text.strip()

    def create_output_folder(self, input_path, output_folder):
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_folder, base_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        return output_path

    def extract_text_from_epub(self, epub_path, keyword, output_folder, num_sentences, direction):
        output_folder = self.create_output_folder(epub_path, output_folder)
        extracted_text = []
        sentences = []
        sentence_page_map = {}

        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith('.xhtml') or file_info.filename.endswith('.html'):
                    with zip_ref.open(file_info) as f:
                        soup = BeautifulSoup(f, 'lxml')
                        text = soup.get_text()
                        page_sentences = self.split_sentences(text)
                        sentences.extend(page_sentences)
                        sentence_page_map.update({i: file_info.filename for i, _ in enumerate(page_sentences, start=len(sentences) - len(page_sentences))})

        keyword_indices = [i for i, s in enumerate(sentences) if keyword.lower() in s.lower()]

        for index in keyword_indices:
            if direction == "Forward":
                selected_sentences = sentences[index:index + num_sentences]
            elif direction == "Backward":
                selected_sentences = sentences[max(0, index - num_sentences + 1):index + 1]

            page_number = sentence_page_map.get(index, 1)
            extracted_text.append(f"KEYWORD FOUND IN {page_number}, SENTENCE {index + 1}:\n{' '.join(selected_sentences)}")

        if extracted_text:
            text_filename = os.path.join(output_folder, "extracted_text.txt")
            with open(text_filename, "w", encoding="utf-8") as text_file:
                cleaned_text = self.clean_text("\n\n".join(extracted_text))
                text_file.write(cleaned_text)

    def extract_text_from_pdf(self, pdf_path, keyword, output_folder, num_sentences, direction):
     with self.interface_action_base_plugin:
        from pypdf import PdfWriter, PdfReader, PageRange
        output_folder = self.create_output_folder(pdf_path, output_folder)
        pdf_document = PdfReader(pdf_path)
        extracted_text = []
        sentences = []
        sentence_page_map = {}

        for page_number, page in enumerate(pdf_document.pages):
            text = page.extract_text()
            if text:
                page_sentences = self.split_sentences(text)
                sentences.extend(page_sentences)
                sentence_page_map.update({i: page_number + 1 for i, _ in enumerate(page_sentences, start=len(sentences) - len(page_sentences))})

        keyword_indices = [i for i, s in enumerate(sentences) if keyword.lower() in s.lower()]

        for index in keyword_indices:
            if direction == "Forward":
                selected_sentences = sentences[index:index + num_sentences]
            elif direction == "Backward":
                selected_sentences = sentences[max(0, index - num_sentences + 1):index + 1]

            page_number = sentence_page_map.get(index, 1)
            extracted_text.append(f"KEYWORD FOUND ON PAGE {page_number}, SENTENCE {index + 1}:\n{' '.join(selected_sentences)}")

        if extracted_text:
            text_filename = os.path.join(output_folder, "extracted_text.txt")
            with open(text_filename, "w", encoding="utf-8") as text_file:
                cleaned_text = self.clean_text("\n\n".join(extracted_text))
                text_file.write(cleaned_text)

    def extract_text(self, input_path, output_folder, keyword, num_sentences, direction):
        file_extension = os.path.splitext(input_path)[1].lower()
        if file_extension == '.pdf':
            self.extract_text_from_pdf(input_path, keyword, output_folder, num_sentences, direction)
        elif file_extension == '.epub':
            self.extract_text_from_epub(input_path, keyword, output_folder, num_sentences, direction)
        else:
            QMessageBox.critical(self.gui, 'Unsupported File Type', 'The selected file is neither a PDF nor an EPUB.')
