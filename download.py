#!/usr/bin/env python3
import os
import json
import lzma
import hashlib
import argparse
import requests

def download_and_decompress(url, hash, filename):

  # check if already downloaded
  if os.path.isfile(filename):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
      for chunk in iter(lambda: f.read(1024*1024), b''):
        sha256.update(chunk)

    if sha256.hexdigest().lower() == hash.lower():
      print("already downloaded ", filename)
      return 0

  size_counter = 0
  dot_counter = 0
  decompressor = lzma.LZMADecompressor(format=lzma.FORMAT_AUTO)
  sha256 = hashlib.sha256()
  with requests.get(url, stream=True, headers={'Accept-Encoding': None}) as download_stream:
    download_stream.raise_for_status()
    size = int(download_stream.headers.get("Content-Length"))
    with open(filename, 'wb') as f:
      for chunk in download_stream.iter_content(chunk_size=1024*1024):
        decompressed_chunk = decompressor.decompress(chunk)
        sha256.update(decompressed_chunk)
        f.write(decompressed_chunk)
        size_counter += len(chunk)

        # Every MB
        if size_counter//(1024*1024) > dot_counter:
          print(f"Downloading '{filename}': {(size_counter*100)//size}%", end='\r')
          dot_counter += 1
  print(f"Downloading '{filename}': 100%")
  assert(sha256.hexdigest().lower() == hash.lower())

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Download AGNOS')
  parser.add_argument('--devel', action='store_true',
                      help='Download AGNOS version used in devel branch')

  args = parser.parse_args()
  if args.devel:
    update_file = "devel.json"
  else:
    update_file = "release.json"

  update = json.load(open(update_file))
  for partition in update:
    download_and_decompress(partition['url'], partition['hash'], f"{partition['name']}.img")
