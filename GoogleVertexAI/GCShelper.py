class gcsLoad(object):
  def __init__(self, project_name = None, bucket_name=None):
      try:
          from google.cloud import storage
      except ImportError:
          raise ImportError(
              "Could not import google-cloud-storage python package. "
              "Please install it with `pip install google-cloud-storage`."
          )
      if project_name and bucket_name:
        self.project_name = project_name
        self.bucket_name = bucket_name
        self.client = storage.Client(project=self.project_name)
        self.bucket = self.client.get_bucket(bucket_name)
      else:
        raise ValueError('Enter project and bucket name')

  def bucket_metadata(self):
    """Prints out a bucket's metadata."""

    print(f"ID: {self.bucket.id}")
    print(f"Name: {self.bucket.name}")
    print(f"Storage Class: {self.bucket.storage_class}")
    print(f"Location: {self.bucket.location}")
    print(f"Location Type: {self.bucket.location_type}")
    print(f"Retention Effective Time: {self.bucket.retention_policy_effective_time}")
    print(f"Retention Period: {self.bucket.retention_period}")
    print(f"Retention Policy Locked: {self.bucket.retention_policy_locked}")
    print(f"Object Retention Mode: {self.bucket.object_retention_mode}")
    print(f"Requester Pays: {self.bucket.requester_pays}")
    print(f"Self Link: {self.bucket.self_link}")
    print(f"Time Created: {self.bucket.time_created}")
    print(f"Labels: {self.bucket.labels}")

  def bucketContents(self, onlyfiles = False):
    """
    Returns contents of buckets , folders and file names as a list
    example:
    ['alteon_syslogs/', 'alteon_syslogs/alteon_syslogs.txt', 'appwall_db/', 'appwall_db/dbe.security.db',
    'userguides/', 'userguides/Alteon CLI User Guide.pdf']
    """

    self.listing = []
    for blob in self.bucket.list_blobs():
      if onlyfiles:
        if blob.name.endswith("/"):
          pass
        else:
          self.listing.append(blob.name)
      else:
        self.listing.append(blob.name)
    return self.listing

  def foldercontents(self, folder=''):
    """Returns blobs. For example
    [<Blob: lab_data_1, userguides/Alteon CLI User Guide.pdf, 1719864729164443>]
    """
    self.docs = []
    if folder == '':
      folder = None
    for blob in self.bucket.list_blobs(prefix=folder): # prefix filters to that folder within bucket
      if blob.name.endswith("/"):
          pass
      else:
        self.docs.append(blob)
    return self.docs

  def downloadFilesMemory(self, folder = None, files = None):
    """Downloads as bytes. For text advised to decode as contents.decode("utf-8")"""
    download = {}
    if folder != None:
      blobsls = self.foldercontents(folder=folder)
    elif files != None and isinstance(files, list):
      blobsls = [self.bucket.blob(i) for i in files]
    else:
      raise ValueError('Provide folder or file names')

    for blob in blobsls:
      contents = blob.download_as_bytes()
      download[blob.name] = contents
    return download

  def downloadFilesLocal(self, folder = None, files = None, destinationFolder ='/content/'):
      filenames = []
      if folder != None:
        blobsls = self.foldercontents(folder=folder)
      elif files != None and isinstance(files, list):
        blobsls = [self.bucket.blob(i) for i in files]
      else:
        raise ValueError('Provide folder or file names')
      assert destinationFolder != '', 'Provide destination path for local download'
      # below is sequential download
      # for multiprocess download check implementation here
      #https://cloud.google.com/storage/docs/downloading-objects#client-libraries-download-object-portion
      for blob in blobsls:
        fname = destinationFolder+blob.name.replace('/','_')
        filenames.append(fname)
        blob.download_to_filename(fname) # cannot write to colab because of /
      return filenames

  def uploadFilesToGCS(self, source_file_name = '', gcsFileName = ''):
      """Placeholder for upload. NOT tested
      """
      assert gcsFileName != '', 'Provide destination file name in GCS bucket'
      assert source_file_name != '', 'Provide source file name'
      blob = self.bucket.blob(gcsFileName)
      generation_match_precondition = 0
      blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)
      print(
          f"File {source_file_name} uploaded to {gcsFileName}."
      )


  def langchainLoader(self, gcsfiles = None, maketempfiles = True, loader_func=UnstructuredFileLoader, custom_metadata={}):
    """takes gcs file names and downloads and creates langchain document objects.
    """

    docs = []
    if gcsfiles != None and isinstance(gcsfiles, list):
      blobsls = [self.bucket.blob(i) for i in gcsfiles]
    if maketempfiles:
      with tempfile.TemporaryDirectory() as temp_dir:
        for blob in blobsls:
          file_path = f"{temp_dir}/{blob.name.replace('/','_')}"
          os.makedirs(os.path.dirname(file_path), exist_ok=True)
          blob.download_to_filename(file_path)
          loader = loader_func(file_path)
          docs.extend(loader.load())
          if custom_metadata:
            for doc in docs:
              doc.metadata.update(custom_metadata)
          else:
            for doc in docs:
                if "source" in doc.metadata:
                    doc.metadata["source"] = f"gs://{self.bucket_name}/{blob.name}"
      return docs



gcs = gcsLoad(project_name = "My Project", bucket_name="lab_data_1")
print (gcs.bucketContents(onlyfiles=True))
#gcs.bucket_metadata()
#docs= gcs.foldercontents(folder="")
#content = gcs.downloadFilesMemory(files=['alteon_syslogs/alteon_syslogs.txt'])
#content = gcs.downloadFilesMemory(folder='alteon_syslogs')
#content = gcs.downloadFilesMemory(folder='appwall_db') 
#gcs.downloadFilesLocal(folder='alteon_syslogs')[]
#documents = gcs.langchainLoader(gcsfiles=['alteon_syslogs/alteon_syslogs.txt'])

