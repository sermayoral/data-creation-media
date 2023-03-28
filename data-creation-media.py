import argparse
import logging
import os
import sys
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

DATE_TIME_ORIG_TAG = 36867

imgFormats = ['png', 'jpg', 'jpeg']
#videoFormats = ['m4v', 'mov', 'mp4']
videoFormats = ['mp4']

logger = logging.getLogger('data-creation-media')

def process(path, year_from):
  for fichero in os.listdir(path):
    filename = os.fsdecode(fichero)
    filepath = os.path.join(path, fichero)
    if os.path.isdir(filepath):
      process(filepath, year_from)
      continue
    nombre_ext = filename.split('.')
    if nombre_ext[-1].lower() == 'py' or filename == '.syncmetadata':
      continue
    valid_media = 0
    if nombre_ext[-1].lower() in imgFormats:
      try:
        im = Image.open(filepath)
        exif = im._getexif()
        im.close()
        if DATE_TIME_ORIG_TAG in exif:
          if not exif[DATE_TIME_ORIG_TAG]:
            valid_media = 2
            logger.info('La fecha de captura de la imagen no esta definida')
          elif int(exif[DATE_TIME_ORIG_TAG][0:4]) < year_from:
            valid_media = 2
            logger.info('Imagen tomada antes del año minimo aceptado')
        else:
          valid_media = 2
          logger.info('No se encuentra la fecha de captura en la imagen')
      except Exception as err:
        valid_media = 3
        logger.error(err)
        
    elif nombre_ext[-1].lower() in videoFormats:
      parser = createParser(filepath)
      if not parser:
        valid_media = 3
        logger.info('Error de parseo de video')
        continue
      with parser:
        try:
          metadata = extractMetadata(parser)
        except Exception as err:
          metadata = None
          logger.error(err)
      if not metadata:
        valid_media = 3
        logger.info('Error al extraer metadatos de video')
        continue
      fecha_creacion_video = None;
      for line in metadata.exportPlaintext():
        if line.split(':')[0] == '- Creation date':
          fecha_creacion_video = line.split(':')[1].split()[0]
          continue
      if fecha_creacion_video and int(fecha_creacion_video[0:4]) < year_from:
        fecha_creacion_video = None
      if not fecha_creacion_video:
        valid_media = 2
        logger.info('No se encuentra la fecha de captura en el video, o su año de captura es menor al aceptado')
    else:
      valid_media = 1
    # Procesamos los errores
    if valid_media > 0:
      if valid_media == 1:
        logger.warning('El archivo %s no es un medio aceptado', filepath)
      elif valid_media == 2:
        logger.warning('El archivo %s no contiene el metadato de fecha de creacion', filepath)
      elif valid_media == 3:
        logger.warning('No se pueden extraer metadatos del archivo %s', filepath)

def parseArguments():
  # Create argument parser
  parser = argparse.ArgumentParser()

  # Positional mandatory arguments
  #parser.add_argument("creditMom", help="Credit mom.", type=float)
  #parser.add_argument("creditDad", help="Credit dad.", type=float)
  #parser.add_argument("debtMom", help="Debt mom.", type=float)

  # Optional arguments
  parser.add_argument("-y", "--year-from", help="Minimum acceptable media year (default 2000)", type=int, default=2000)
  parser.add_argument("-l", "--log-level", help="Set log level", type=str, default='WARNING')

  # Print version
  #parser.add_argument("--version", action="version", version='%(prog)s - Version 1.0')

  # Parse arguments
  return parser.parse_args()

if __name__ == '__main__':
  # Parse the arguments
  args = parseArguments()
  # Set logging
  logging.basicConfig(level=args.log_level.upper())
  # Process media
  process('.', args.year_from)

