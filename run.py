from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, RedirectResponse

from fastai.vision import ImageDataBunch, create_cnn, open_image, get_transforms, imagenet_stats, models, show_image
from pathlib import Path

from io import BytesIO

import sys
import uvicorn
import aiohttp
import asyncio
from PIL import Image as PILImage
from fastai.vision import image2np
import base64

def encode(img):
    img = (image2np(img.data) * 255).astype('uint8')
    pil_img = PILImage.fromarray(img)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    return base64.b64encode(buff.getvalue()).decode("utf-8")

async def get_bytes(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()


app = Starlette()

path = Path('data/')

classes = ['pop/rap','rock/heavy-metal']
data2 = ImageDataBunch.single_from_classes(path, classes, tfms=get_transforms(), size=224).normalize(imagenet_stats)
learn = create_cnn(data2, models.resnet50, pretrained=False)
learn.load('resnet-50-2-classes-3975-im-stage-2')

index_html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Album-art genre classifier</title>

    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

  </head>

  <body class="bg-light">

    <div class="container">
      <div class="py-5 text-center">
        <h2>Album-art genre classifier</h2>
        <p class="lead">This is an image classifier API that takes in an image of an album cover and returns a prediction of the genre of the album.</p>
        <p>Currently supports classification in Rock/Heavy Metal or Pop/Rap</p>
        
      </div>
<div class="row justify-content-center">
    <div class="col-6">
      
      <form  action="/upload" method="post" enctype="multipart/form-data">
        <h4 class="mb-3">Select image to upload:</h4>
        <div class="form-group">
            <input type="file" name="file">
            <input type="submit" value="Upload Image">
        </div>
        </form>
      
      <br><br>
      <h4 class="mb-3">Or submit a URL::</h4>
        
        <form action="/classify-url" method="get">
            <input type="url" name="url">
            <input type="submit" value="Fetch and analyze image">
      </form>
          
  </div>
  </div>
      <br><br>
     <div align="center" class="row justify-content-center">
       <div class="col-4">
         <p>Rock/HM example:</p>
         <a href=""><img width=300px src="http://wwwcdn.goldminemag.com/wp-content/uploads/2011/05/Savage_LooseNLethal.jpg"></a>
       </div>
    <div class="col-4">
      <p>Pop/rap example:</p>
      <a href=""><img width=300px src="http://4.bp.blogspot.com/-ixz9_hrHt40/USZmiaQaytI/AAAAAAAACI8/sCsxhAZvwUE/s1600/R-149119-1279003359.jpeg"></a>
    </div>
  </div>
        
<div class="row justify-content-center">
      <footer class="my-5 pt-5 text-muted text-center text-small">
        <p class="mb-1">Made by <a target="_" href="https://github.com/dhth/">dhruv</a></p>
        <ul class="list-inline">
          <li class="list-inline-item"><a target="_" href="https://github.com/dhth/album-art-genre-classifier">source</a></li>
        </ul>
      </footer>
    </div>
    </div>
  </body>
</html>
"""


resp_html = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Album-art genre classifier</title>

    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

  </head>

  <body class="bg-light">

    <div class="container">
      <div class="py-5 text-center">
        <h2>Album-art genre classifier</h2>
        <p class="lead">This is an image classifier API that takes in an image of an album cover and returns a prediction of the genre of the album.</p>
        <p>Currently supports classification in Rock/Heavy Metal or Pop/Rap</p>
                <br>
                <figure class="figure">
                <img style="max-width:500px;" src="data:image/png;base64, {}" class="figure-img img-thumbnail input-image">
                </figure>

        <p class="lead">It appears to be <b>{}</b></p>
        <p class="lead"><a href="/">go back</a></p>
        
      </div>
        
<div class="row justify-content-center">
      <footer class="my-5 pt-5 text-muted text-center text-small">
        <p class="mb-1">Made by <a target="_" href="https://github.com/dhth/">dhruv</a></p>
        <ul class="list-inline">
          <li class="list-inline-item"><a target="_" href="https://github.com/dhth/album-art-genre-classifier">source</a></li>
        </ul>
      </footer>
    </div>
    </div>
  </body>
</html>
"""




@app.route("/upload", methods=["POST"])
async def upload(request):
    data = await request.form()
    bytes = await (data["file"].read())
    return predict_image_from_bytes(bytes)


@app.route("/classify-url", methods=["GET"])
async def classify_url(request):
    bytes = await get_bytes(request.query_params["url"])
    return predict_image_from_bytes(bytes)


def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    pred_class,pred_idx,outputs = learn.predict(img)
    img_data = encode(img)
    return HTMLResponse(resp_html.format(img_data, str(pred_class)))
    #return JSONResponse({
    #    "prediction": pred_class
    #})



@app.route("/")
def form(request):
    return HTMLResponse(index_html)


@app.route("/form")
def redirect_to_homepage(request):
    return RedirectResponse("/")


if __name__ == "__main__":
    if "serve" in sys.argv:
        uvicorn.run(app, host="0.0.0.0", port=8008)
