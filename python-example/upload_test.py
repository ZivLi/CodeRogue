@route("/offers/banner_img")
class Upload(View):

    def post(self):
        upload_path = os.path.join(os.path.dirname(__file__), 'upload/')
        resp = self.request.files['files[]'][0]
        body = resp['body']
        ext = os.path.splitext(resp['filename'])[1]
        cname = str(hashlib.md5(body).hexdigest()) + ext
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
        url_obj = ImgUrl.find_one({'cname': cname})
        if not url_obj:
            fpath = upload_path + cname
            f = open(fpath, 'w')
            f.write(body)
            u = UploadS3(fpath, cname)
            res = u.upload_start()
            if res.done():
                url = 'https://leadhugstatic.s3.amazonaws.com/' + cname
                img = ImgUrl(dict(
                    _id=gid('leadhug_imgUrl'),
                    url=url,
                    cname=cname
                )
                )
                img.save()
            else:
                url = "Upload failure!"
            os.remove(fpath)
        else:
            url = url_obj.url
        self.finish(dict(url=url))
