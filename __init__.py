from calibre.customize import InterfaceActionBase

class PDFTextExtractorPlugin(InterfaceActionBase):
    name = 'PDF and EPUB Processor'
    description = 'Process PDF and EPUB files'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Hoàng Minh Quân'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 7, 53)
    actual_plugin = 'calibre_plugins.pdf_text_extractor.main:PDFTextExtractorInterface'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.pdf_text_extractor.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
