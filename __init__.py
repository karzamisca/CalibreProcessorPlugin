from calibre.customize import InterfaceActionBase #Built-in for Calibre 7.17

class InterfacePluginDemo(InterfaceActionBase):
    name = 'Text-based PDF and EPUB Processor Calibre Plugin'
    description = 'Process Text-based PDF and EPUB files'
    supported_platforms = ['windows', 'osx', 'linux']
    author = 'Hoàng Minh Quân'
    version = (1, 0, 0)
    minimum_calibre_version = (0, 7, 53)
    actual_plugin = 'calibre_plugins.text_based_pdf_and_epub_processor.main:InterfacePlugin'

    def is_customizable(self):
        return True

    def config_widget(self):
        from calibre_plugins.text_based_pdf_and_epub_processor.config import ConfigWidget
        return ConfigWidget()

    def save_settings(self, config_widget):
        config_widget.save_settings()
        ac = self.actual_plugin_
        if ac is not None:
            ac.apply_settings()
