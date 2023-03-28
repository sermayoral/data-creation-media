import os
import sys
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

DATE_TIME_ORIG_TAG = 36867

imgFormats = ['png', 'jpg', 'jpeg']
#videoFormats = ['m4v', 'mov', 'mp4']
videoFormats = ['mp4']

def process(path):
  for fichero in os.listdir(path):
    filename = os.fsdecode(fichero)
    filepath = os.path.join(path, fichero)
    if os.path.isdir(filepath):
      process(filepath)
      continue
    nombre_ext = filename.split('.')
    if nombre_ext[-1].lower() == 'py' or filename == '.syncmetadata':
      continue
    if nombre_ext[-1].lower() in imgFormats:
      #print('Imagen', filepath)
      try:
        im = Image.open(filepath)
        exif = im._getexif()
        im.close()
        if DATE_TIME_ORIG_TAG in exif:
          if not exif[DATE_TIME_ORIG_TAG]:
            print('! La imagen', filepath, 'no contiene el metadato de fecha de creacion')
        else:
          print('! La imagen', filepath, 'no contiene el metadato de fecha de creacion')
      except:
        print('! No se puede extraer metadatos a la imagen', filepath)
    elif nombre_ext[-1].lower() in videoFormats:
      parser = createParser(filepath)
      if not parser:
        print('! No se puede parsear el video', filepath)
        continue
      with parser:
        try:
          metadata = extractMetadata(parser)
        except Exception as err:
          metadata = None
      if not metadata:
        print('! No se puede extraer metadatos del video', filepath)
        continue
      fecha_creacion_video = None;
      for line in metadata.exportPlaintext():
        if line.split(':')[0] == '- Creation date':
          fecha_creacion_video = line.split(':')[1].split()[0]
          continue
      if fecha_creacion_video and int(fecha_creacion_video[0:4]) < 1980:
        fecha_creacion_video = None
      if not fecha_creacion_video:
        print('! El video', filepath, 'no contiene el metadato de fecha de creacion')
    else:
      print('! El archivo', filepath, 'no es un medio aceptado')

process('.')

