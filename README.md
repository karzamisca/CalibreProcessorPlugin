### Text-based PDF and Epub Processor Calibre Plugin

## Classes and Functions Overview

### `InterfacePluginDemo` (in `__init__.py`)

**Purpose:** This class defines metadata and configuration for the Calibre plugin, such as name, description, supported platforms, and version.

- **`name`**: The name of the plugin.
- **`description`**: A brief description of what the plugin does.
- **`supported_platforms`**: Platforms on which the plugin can run (e.g., 'windows', 'osx', 'linux').
- **`author`**: The author of the plugin.
- **`version`**: The version of the plugin.
- **`minimum_calibre_version`**: The minimum Calibre version required.
- **`actual_plugin`**: The path to the main plugin implementation.

**Functions:**

- **`is_customizable()`**: Returns `True` if the plugin has customizable settings.
- **`config_widget()`**: Returns the configuration widget for the plugin.
- **`save_settings(config_widget)`**: Saves settings from the configuration widget.

### `InterfacePlugin` (in `main.py`)

**Purpose:** This class provides the core functionality for processing PDF and EPUB files and integrates with the Calibre interface.

**Functions:**

- **`genesis()`**: Initializes the plugin action and connects it to the user interface.
- **`show_dialog()`**: Displays the configuration dialog.
- **`split_sentences(text)`**: Splits a given text into sentences.
- **`clean_text(text)`**: Cleans up the text by removing extra newlines and spaces.
- **`create_output_folder(input_path, output_folder)`**: Creates an output folder for storing results.
- **`extract_text_from_epub(epub_path, keyword, output_folder, num_sentences, direction)`**: Extracts text from EPUB files, focusing on sentences around a specified keyword.
- **`extract_text_from_pdf(pdf_path, keyword, output_folder, num_sentences, direction)`**: Extracts text from PDF files, focusing on sentences around a specified keyword.
- **`extract_images_from_pdf(pdf_path, output_folder)`**: Extracts images from PDF files.
- **`extract_images_from_epub(epub_path, output_folder)`**: Extracts images from EPUB files.
- **`extract_text(input_path, output_folder, keyword, num_sentences, direction, extract_text, extract_images)`**: Extracts text and/or images from a file or folder based on user options.
- **`search_text_in_pdf(pdf_path, keyword, num_sentences, direction)`**: Searches for a keyword in a PDF file and returns the surrounding text.
- **`search_text_in_epub(epub_path, keyword, num_sentences, direction)`**: Searches for a keyword in an EPUB file and returns the surrounding text.
- **`search_text(input_path, keyword, num_sentences, direction)`**: Searches for a keyword in a file (PDF or EPUB) and returns the surrounding text.

### `TextBasedPDFandEpubProcessorDialog` (in `ui.py`)

**Purpose:** This class defines the user interface dialog for the plugin, allowing users to configure and execute text and image extraction tasks.

**Functions:**

- **`__init__(self, gui, icon, do_user_config)`**: Initializes the dialog, setting up UI elements and connections.
- **`update_input_button()`**: Updates the text on the input button based on the selected input type.
- **`select_input_file_or_folder()`**: Opens a file or folder dialog based on user selection.
- **`select_output_dir()`**: Opens a directory dialog to select the output directory.
- **`extract_text()`**: Triggers text and/or image extraction based on user settings.
- **`search_and_display_text()`**: Searches for a keyword in selected files and displays the results.
- **`config()`**: Placeholder function for configuring the plugin (not implemented).

