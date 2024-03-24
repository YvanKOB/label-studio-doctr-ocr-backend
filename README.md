# label-studio-doctr-ocr-backend
The aim of this repository is to create and make available an image text annotation tool based on Doctr OCR.

### Launch Label Studio

Begin by installing Label Studio using Docker. You have two options for how you want to handle your image data. The first option is local file storage, where you upload the images directly to Label Studio and then serve the images to the doctr ocr ML Backend directly from Label Studio. While this solution is an easy way to start working with your data immediately, it is recommended for something other than production usage. To use local file storage, start Label Studio with the following command:

```bash
docker pull heartexlabs/label-studio:latest

docker run -it \
    -p 8080:8080 \
    -v `pwd`/mydata:/label-studio/data \
    --env LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true \
    --env LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/label-studio/data/images \
    heartexlabs/label-studio:latest
```

This will pull the latest image of Label Studio to your system, launch it inside Docker, and assign it to port 8080.

The second option is to use cloud storage, such as S3, GCP or Azure. Cloud storage offers a secure connection, easy data management, automated task synchronisation and integrates more easily into your machine learning pipeline. Here we'll draw on the Tesseract ML Backend example for Doctr OCR ML Backend, which will include a local Minio installation that replicates the S3 API, allowing you to experiment without having to set up a commercial cloud storage offering. If you opt for cloud storage, you can launch Label Studio using this command:

```bash
docker pull heartexlabs/label-studio:latest

docker run -it \
    -p 8080:8080 \
    -v `pwd`/mydata:/label-studio/data \
    heartexlabs/label-studio:latest
```

![Installing and Running Label Studio using Docker](https://labelstud.io/_astro/531022f187f3bc2504bc64d62ff33901d7e44c1e-1788x1670_Z2ihqbl.avif)


### Set Up The OCR Project

Once Label Studio has launched, open your browser (we suggest using Chrome, as it provides the best compatibility with the Label Studio frontend) and navigate to http://localhost:8080. This will bring you to the Label Studio login page, where you can create a new account and log in to the Label Studio Platform.

![The Label Studio Login Screen](https://labelstud.io/_astro/815861a88ce0bb8113f3e4917747ea174503376b-1784x908_xHD9F.avif)

Select “Create” to start a new project.
!["Heidi doesn't see any projects here"](https://labelstud.io/_astro/4ce40fa6562086ca606fd9d080853225168c481b-1784x942_Z18PddP.avif)

In the “Project Name” tab, name the project " Tesseract OCR. " If you’re using the local file storage option, you can upload your image data into the “Data Import” tab.
 
![The New Project Dialog](https://github.com/YvanKOB/label-studio-doctr-ocr-backend/blob/doctr-ml-backend/Capture%20d%E2%80%99e%CC%81cran%202024-03-24%20a%CC%80%2006.02.06.png)

In the Labeling Setup tab, choose “Custom template” and paste the following labeling interface, defined using XML, into the “Code” polygon.

```xml


```
(to do --> I don't know how to custom the templates)

You will see a visual representation of the labeling interface. Select “Save,” and you’ll be taken to the data manager page for the project.

![The Custom OCR Labeling Interface](https://labelstud.io/_astro/ca7761f5e7e35f35f71a36a694c9ae7edb064125-1784x846_Z2pxXhi.avif)
Image I need to change


If you’re using local file storage, select the user settings icon in the top–right corner of the interface, select “Accounts & Settings,” and copy the Access Token. You’ll need this to launch the model.
![The Label Studio API Access Token](https://labelstud.io/_astro/d5be43025ec9d2ce0951c6e38c53f006d7805296-1804x974_Z27rETI.avif)

### Download and Configure Label Studio ML Backend

Open up a terminal window, and download the Label Studio Machine Learning Backend repository:

```bash
git clone https://github.com/YvanKOB/label-studio-doctr-ocr-backend.git
```

Open the example.env file in your favorite text editor and fill in the required variables. If using local file storage, fill in the LABEL_STUDIO_ACCESS_TOKEN you copied from the previous step. If you’re setting up cloud storage using the Minio example, you must fill in the AWS access tokens and Minio credentials with your preferred username and password (the password must be at least eight characters long). When you’re done with the configuration, save and exit.

![Configure the ML Backend and Minio](https://labelstud.io/_astro/eb49b0fd3c75e1f51148839be575de6eb9588a88-1796x986_Zx3ls3.avif)

### Launch the Doctr OCR ML Backend

1. You’re now ready to build and start Machine Learning backend on `http://localhost:9090`. If you opted to use local storage, use the command:

```bash
docker-compose up doctr-backend
```

2. Validate that backend is running

```bash
$ curl http://localhost:9090/health
{"status":"UP"}
```

If you opted to use the cloud storage example, run the command:
```bash
docker-compose up
```

This will launch both the Doctr OCR Backend and the Minio server. You can verify that the Minio console is running at http://localhost:9001/.

![Starting Minio and the ML Backend](https://labelstud.io/_astro/5ac07d3b2f92c3705342e000910f61ab05e32c7d-1796x1370_1EOhDN.avif)
 **I Need to change the image with Doctr OCR**

### A Quick Note About Host URLs and Docker

When running services locally using Docker, it’s convenient to access them from your browser using the hostname localhost, which is used as a standard shorthand for the system address you’re accessing from. However, this convenience can break down when you want to direct Docker-hosted services to access other services on the same machine. When you use the localhost convention from inside a Docker container, it refers to the network address of the container itself rather than the host system.

This frequently leads to errors where you configure Label Studio to access a machine learning backend using the hostname localhost. If you’re running Label Studio in Docker, this will lead to errors, as Label Studio’s interpretation of localhost differs from yours.

Thankfully, there are two easy workarounds to this problem. The first is to use your computer's IP address. This tells Label Studio the direct address of where the ML backend containers are located.

The second is to use a Docker-provided hostname that connects to the host machine: host.docker.internal. For this post, we will use the host.docker.internal convention. In some instances (usually when running Docker on Linux), this convenience may not be available, and we suggest you fall back to using the direct IP if you’re running into errors.


### Upload Images to Cloud Storage


If you opted to use cloud storage, log into the Minio console at http://localhost:9001.
![The Minio Login Screen](https://labelstud.io/_astro/18699b990772380b330f9c697fe2c4afb87f4dd0-1790x822_uPKFy.avif)



Create a new bucket with the name “doctr.”
![Creating a Bucket](https://labelstud.io/_astro/3ebaae23d860ef295215f449c6f1679bb974191d-1790x860_1xNLWM.avif)



Select “browse bucket, " upload your files to the cloud storage, and return to the Label Studio interface.
![Uploading Files to the Bucket](https://labelstud.io/_astro/3b2d2eb19fa9175b5c263a128ff2f72e25528f32-1790x750_Z1lSo7L.avif)


Navigate back to the Doctr OCR project, then select “Settings.” Select the “Cloud Storage” tab, then “Add Source Storage.” In the “Bucket Name” field, enter the name you set in the previous step, “tesseract.” For the S3 endpoint, use the address http://host.docker.internal:9000. Set the Access Key ID to your Minio username and the “Secret Access Key” to your Minio password. Toggle “Treat every bucket object as a source file,” toggle “Use pre-signed URLs” to off, and select “Check Connection.” The dialogue should say, “Successfully connected!” Select "Add Storage.”
![Adding Cloud Storage to Label Studio](https://labelstud.io/_astro/55edbfbeca424b27d1eedd3603913899a9c628a7-1790x1632_g3V80.avif)


Finally, select “Sync Storage,” and you will see that your tasks have been imported into Label Studio.
![Syncing Cloud Storage Tasks to Label Studio](https://labelstud.io/_astro/f840306caa712afab84c0e769b80bdda6169dbe9-1790x1018_25JPIy.avif)


Configure the ML Backend Connection

From the Doctr OCR project settings, select “Machine Learning. " Select “Add Model,” set the “Title” to “Doctr, " and the URL to “http://host.docker.internal:9090. " Toggle “Use for interactive preannotations” to on, then select “Validate and Save.”

![Add Doctr Model to Label Studio](https://github.com/YvanKOB/label-studio-doctr-ocr-backend/blob/doctr-ml-backend/Capture%20d%E2%80%99e%CC%81cran%202024-03-24%20a%CC%80%2006.37.57.png)

The dialog will show that the model is connected. Select “Save.”

![Saving the Tesseract Model to Label Studio](https://github.com/YvanKOB/label-studio-doctr-ocr-backend/blob/doctr-ml-backend/Capture%20d%E2%80%99e%CC%81cran%202024-03-24%20a%CC%80%2006.41.33.png)


### Start Labeling!

With all the setup and configuration completed, we can start labeling data. Navigate back to the project data manager by selecting the path at the top of the Label Studio interface, “Projects / Doctr OCR.”
![Navigating to the Data Manager](https://labelstud.io/_astro/51ac522ff6531e87b1d8d4dd2945ab9b435a9b72-2508x1104_IbSqm.avif)


Select “Label All Tasks.” You’ll be presented with an image that has your data and three label options. Toggle “Auto-Annotation” to on, then make sure that “Auto accept annotation suggestions” is checked.
![The OCR Labeling Interface](https://labelstud.io/_astro/c366355f14c45077e2c029885beaa6f4444f3b3c-1432x1548_Z23YwHF.avif)


Select the “Auto Detect” bounding box (the purple square on the toolbar).
![Enabling the Auto-Detect Polygon Tool](https://labelstud.io/_astro/7d8e4dffa0573a87950cc429799a911293999b3e-1548x848_1GDfcp.avif)


Select the label you want to apply (you can use the hotkeys ‘1’, ‘2’, or ‘3’ to help speed that process), then draw a bounding box around the text you want to generate a label for. On the right side of the labeling interface, you’ll see the predicted text assigned to the label and bounding box you just applied. You can edit the prediction within this text box.
![Automated Labeling with Doctr OCR!](https://labelstud.io/_astro/798e241beed0d47b0fbdcca6304d840e98aa6f6a-1432x1592_ZB0p9g.avif)


If you’re satisfied with the result, hit the “Submit” button to save the annotation and move on to the next task. Congratulations! You’ve just built an automated annotation workflow that combines the power of Doctr OCR with the expertise of human annotators.


### Digging a bit Deeper

When you’re ready to connect your cloud storage, you will want to modify the ML backend to connect to your images securely. The load_image method in the `doctr_labeling.py.py` file is a good starting point for understanding how to attach your cloud storage to an ML backend.

```python
def load_image(img_path_url):
    # load an s3 image, this is very basic demonstration code
    # you may need to modify to fit your own needs

    if img_path_url.startswith("s3:"):
        bucket_name = img_path_url.split("/")[2]
        key = "/".join(img_path_url.split("/")[3:])
        obj = S3_TARGET.Object(bucket_name, key).get()
        data = obj['Body'].read()
        image = Image.open(io.BytesIO(data))
        return image
    else:
        filepath = get_image_local_path(img_path_url,
        label_studio_access_token=LABEL_STUDIO_ACCESS_TOKEN,
            label_studio_host=LABEL_STUDIO_HOST)
        return Image.open(filepath)
```

This example is designed to get you up and running with an example annotation task.


**This README draws heavily on the tutorial from 29 January 2024, entitled: Interactive OCR with Tesseract and Label Studio, from Label Studio's blog on Tesseract OCR. You can find the original tutorial at this address: [Interactive OCR with Tesseract and Label Studio](https://labelstud.io/blog/interactive-ocr-with-tesseract-and-label-studio/)**
