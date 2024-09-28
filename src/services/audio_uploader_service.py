from flask import jsonify, request, send_file
from bson import ObjectId
import io

import base64

def upload_audio(_mongod, _gridfs):
    try:
        # Obtener el JSON completo del request
        data = request.get_json()

        # Validar la estructura del JSON
        if 'data' not in data or 'audioBase64' not in data['data']:
            return jsonify({'error': 'Falta el campo "audioBase64" en "data"'}), 400

        if 'metadata' not in data or not all(k in data['metadata'] for k in ['mimetype', 'extension', 'filename']):
            return jsonify({'error': 'Falta información en el campo "metadata"'}), 400

        # Extraer el audio y decodificar el Base64 a binario
        audio_base64 = data['data']['audioBase64']
        audio_data = base64.b64decode(audio_base64)

        # Extraer los metadatos del audio
        mimetype = data['metadata']['mimetype']
        extension = data['metadata']['extension']
        filename = data['metadata']['filename']
        size = data['metadata'].get('size')  # Tamaño es opcional
        size_unit = data['metadata'].get('sizeUnit')  # Unidad opcional

        # Crear un nombre de archivo completo
        full_filename = f"{filename}.{extension}"

        # Subir el archivo a GridFS
        file_id = _gridfs.put(audio_data, filename=full_filename, content_type=mimetype)

        # Responder con el ID del archivo subido y los metadatos
        return jsonify({
            'message': 'Archivo subido correctamente',
            'file_id': str(file_id),
            'metadata': {
                'filename': full_filename,
                'mimetype': mimetype,
                'size': size,
                'sizeUnit': size_unit
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def get_audio_file(file_id, _gridfs):
    try:
        # Intenta encontrar el archivo en GridFS
        file_data = _gridfs.find_one({"_id": ObjectId(file_id)})

        if not file_data:
            return jsonify({'error': 'Archivo no encontrado'}), 404

        # Recuperar el archivo y enviarlo
        output = _gridfs.get(file_data._id).read()
        return send_file(io.BytesIO(output), mimetype=file_data.content_type, as_attachment=True, download_name=file_data.filename)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
