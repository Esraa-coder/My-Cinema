import os
allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(fileName):
     return '.' in fileName and fileName.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_size(file):
    original_position = file.tell()
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(original_position)
    return file_size <= 6 * 1024 * 1024 #6MB