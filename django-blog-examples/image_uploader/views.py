from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from PIL import Image
from django.views.generic.edit import FormView
from django.views.generic import View
from django.views.generic import ListView
from django.views.generic import DetailView
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from .forms import UploadURLForm
from .utils import *
from .models import UploadedImage

import StringIO


@csrf_exempt
def UploadImg(request):
	if request.method == 'POST':
		if 'file' in request.FILES:
			file = request.FILES['file']
			filename = file._name
			#fobject = StringIO.StringIO()
			fobject = open('%s/%s' % ("inoimg", filename) , 'wb')
			for chunk in file.chunks():
                            fobject.write(chunk)
			fobject.close()
                        pil_image = Image.open('%s/%s' % ("inoimg", filename))
                        #pil_image = Image.open(fobject)
                        django_file = pil_to_django(pil_image)
                        uploaded_image = UploadedImage()
                        uploaded_image.image.save(filename, django_file)
                        uploaded_image.save()
			return HttpResponse('File Uploaded')
	return HttpResponse('Failed to Upload File')


class UploadURLView(FormView):
    form_class = UploadURLForm
    template_name = "image_uploader/upload.html"

    def get_success_url(self):
        return reverse("upload-detail", args=[self.uploaded_image.pk, ])

    def form_valid(self, form):
        def _invalidate(msg):
            form.errors['url'] = [msg, ]
            return super(UploadURLView, self).form_invalid(form)

        url = form.data['url']
        domain, path = split_url(url)
        filename = get_url_tail(path)

        if not image_exists(domain, path):
            return _invalidate(_("Couldn't retreive image. (There was an error reaching the server)"))

        fobject = retrieve_image(url)
        if not valid_image_mimetype(fobject):
            return _invalidate(_("Downloaded file was not a valid image"))

        pil_image = Image.open(fobject)
        if not valid_image_size(pil_image)[0]:
            return _invalidate(_("Image is too large (> 4mb)"))
        django_file = pil_to_django(pil_image)
        self.uploaded_image = UploadedImage()
        self.uploaded_image.image.save(filename, django_file)
        self.uploaded_image.save()
        return super(UploadURLView, self).form_valid(form)

class ImgListView(ListView):
    model = UploadedImage
    template_name = "image_uploader/imglist.html"


class UploadDetailView(DetailView):
    model = UploadedImage
    context_object_name = "image"
    template_name = "image_uploader/detail.html"
