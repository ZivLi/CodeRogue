from flask import send_from_directory, send_file
from tempfile import NamedTemporaryFile, TemporaryDirectory
import zipfile
from io import BytesIO



class DownloadFileService:

    def __init__(self, files):
        # Please attention to the type.
        self.files = files   #Type of self.files here is BytesIOof files.

    def _download(self):
        if isinstance(self.files, list):
            return self._download_many()
        else:
            return self._download_single()

    def _download_single(self):
        # Using temporary file to save files with delete auto.
        with NamedTemporaryFile('w+b', delete=True) as tf:
            tf.write(self.files.read())
            response = send_from_directory(*os.path.split(tf.name), as_attachment=True)
            response.headers['Content-Disposition'] = "attachment; filename=" + f'{self.files.name}.png'
            return response

    def _download_many(self):
        # Using temporary directory
        with TemporaryDirectory() as td:
            for _file in self.files:
                filename = td + f"{_file.name}.png"
                with open(filename, 'w+b') as temp_file:
                    pass
            memory_file = BytesIO()
            with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                for _file in self.files:
                    with open(td + f"{_file.name}.png", 'rb') as fp:
                        zf.writestr(f"{_file.name}.png", fp.read())
            memory_file.seek(0)
            send_file(memory_file, as_attachment=True)
