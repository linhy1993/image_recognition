import io
import os

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from gtts import gTTS
Description = ''

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='/Users/linhongyi/Desktop/google_application_credentials.json'
# Instantiates a client
client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
file_name = os.path.join(
    os.path.dirname(__file__),
    '/Users/linhongyi/PycharmProjects/project_6313/todo-api/images/111.png111.png')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

# Performs label detection on the image file
response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)
    Description = Description+label.description+' '

print(Description)

tts = gTTS(text=Description, lang='en')
tts.save("/Users/linhongyi/PycharmProjects/project_6313/todo-api/images/test.mp3")