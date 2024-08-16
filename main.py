import re
import os
import zipfile
from bs4 import BeautifulSoup
from PyQt5.QtGui import QImage
from calibre.gui2.actions import InterfaceAction
from calibre_plugins.pdf_text_extractor.ui import PDFTextExtractorDialog
from PyQt5.QtWidgets import QMessageBox

class PDFTextExtractorInterface(InterfaceAction):
    name = 'PDF and EPUB Processor'

    action_spec = ('PDF and EPUB Processor', None, 'Process PDF and EPUB files', 'Ctrl+Shift+E')

    def genesis(self):
        icon = get_icons('images/icon.png', 'PDF and EPUB Processor')
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

    def extract_images_from_pdf(self, pdf_path, output_folder):
     with self.interface_action_base_plugin:
        from pypdf import PdfWriter, PdfReader, PageRange
        output_folder = self.create_output_folder(pdf_path, output_folder)
        pdf_document = PdfReader(pdf_path)

        image_folder = os.path.join(output_folder, "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        for page_number, page in enumerate(pdf_document.pages):
            for image_index, image in enumerate(page.images):
                image_name = f"image_page{page_number + 1}_{image_index + 1}.png"
                image_path = os.path.join(image_folder, image_name)
                image_data = QImage.fromData(image.data)
                if not image_data.save(image_path):
                    print(f"Failed to save image: {image_name}")

    def extract_images_from_epub(self, epub_path, output_folder):
        output_folder = self.create_output_folder(epub_path, output_folder)
        image_folder = os.path.join(output_folder, "images")
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)
        
        with zipfile.ZipFile(epub_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_path = os.path.join(image_folder, os.path.basename(file_info.filename))
                    with zip_ref.open(file_info) as img_file, open(image_path, 'wb') as out_file:
                        out_file.write(img_file.read())

    def extract_text(self, input_path, output_folder, keyword, num_sentences, direction, extract_text, extract_images):
        file_extension = os.path.splitext(input_path)[1].lower()

        if os.path.isdir(input_path):
            for file_name in os.listdir(input_path):
                full_path = os.path.join(input_path, file_name)
                if file_name.lower().endswith('.pdf') or file_name.lower().endswith('.epub'):
                    if file_extension == '.pdf':
                        if extract_text:
                            self.extract_text_from_pdf(full_path, keyword, output_folder, num_sentences, direction)
                        if extract_images:
                            self.extract_images_from_pdf(full_path, output_folder)
                    elif file_extension == '.epub':
                        if extract_text:
                            self.extract_text_from_epub(full_path, keyword, output_folder, num_sentences, direction)
                        if extract_images:
                            self.extract_images_from_epub(full_path, output_folder)
        else:
            if file_extension == '.pdf':
                if extract_text:
                    self.extract_text_from_pdf(input_path, keyword, output_folder, num_sentences, direction)
                if extract_images:
                    self.extract_images_from_pdf(input_path, output_folder)
            elif file_extension == '.epub':
                if extract_text:
                    self.extract_text_from_epub(input_path, keyword, output_folder, num_sentences, direction)
                if extract_images:
                    self.extract_images_from_epub(input_path, output_folder)
            else:
                QMessageBox.critical(self.gui, 'Unsupported File Type', 'The selected file is neither a PDF nor an EPUB.')

    def search_text_in_pdf(self, pdf_path, keyword, num_sentences, direction):
     with self.interface_action_base_plugin:
        from pypdf import PdfReader
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
        cleaned_text = self.clean_text("\n\n".join(extracted_text))
        return cleaned_text

    def search_text_in_epub(self, epub_path, keyword, num_sentences, direction):
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

            page_number = sentence_page_map.get(index, "unknown page")
            extracted_text.append(f"KEYWORD FOUND IN {page_number}, SENTENCE {index + 1}:\n{' '.join(selected_sentences)}")
        cleaned_text = self.clean_text("\n\n".join(extracted_text))
        return cleaned_text

    def search_text(self, input_path, keyword, num_sentences, direction):
        file_extension = os.path.splitext(input_path)[1].lower()

        if file_extension == '.pdf':
            return self.search_text_in_pdf(input_path, keyword, num_sentences, direction)
        elif file_extension == '.epub':
            return self.search_text_in_epub(input_path, keyword, num_sentences, direction)
        else:
            return 'Unsupported file type. Please select a PDF or EPUB file.'

