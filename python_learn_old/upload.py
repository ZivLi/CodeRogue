import tornado.ioloop
import tornado.web
import shutil
import os


class UploadFileHandler(tornado.web.RequestHandler):

    def get(self):
        self.write('''
<html>
	<head><title>Upload File</title></head>
	<body>
		<form action='file' enctype='multipart/form-data' method='post'>
		<input type='file' name='file'/><br/>
		<input type='submit' value='submit'/>
		</form>
	</body>
</html>
''')

    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__), 'files')
        file_metas = self.request.files['file']
        for meta in file_metas:
            filename = meta['filename']
            filepath = os.path.join(upload_path, filename)
            with open(filepath, 'wb') as up:
                up.write(meta['body'])
            self.write('finished')

app = tornado.web.Application([
	(r'/file', UploadFileHandler),
])

if __name__ == '__main__':
	app.listen(3000)
	tornado.ioloop.IOLoop.instance().start()