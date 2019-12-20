import dropbox
import requests
from concurrent.futures.thread import ThreadPoolExecutor

from image_collection import Image, ImageCollection

import logzero
import logging
from logzero import logger

import settings


dbx = None
to_batch = []

def main():
    global dbx
    global to_batch

    logger.info("starting...")


    dbx = dropbox.Dropbox(settings.DROPBOX_ACCESS_TOKEN)

    logger.info("logged into Dropbox")

    for folder_entry in dbx.files_list_folder(settings.PARENT_FOLDER).entries:
        to_batch.clear()
        ingest_folder(folder_entry)
        logger.info(f"we now have {len(to_batch)} items to commit to DLCS in batches of {settings.BATCH_SIZE}")
        process_batches(create_batches())

    logger.info("done")


def chunks(source, chunk_size):
    """Yield successive n-sized chunks from l."""
    # https://stackoverflow.com/a/312464

    for i in range(0, len(source), chunk_size):
        yield source[i:i + chunk_size]


def process_batches(batches):
    logger.info(f"processing {len(batches)} batches")

    authorisation = requests.auth.HTTPBasicAuth(settings.DLCS_API_KEY_ID, settings.DLCS_API_SECRET_KEY)
    url = settings.DLCS_API_BASE + '/customers/' + str(settings.DLCS_CUSTOMER_ID) + '/queue'

    index = 1
    for batch in batches:
        logger.info(f"committing batch {index} of {len(batches)}")
        images = ImageCollection(images=batch)
        json = images.as_json()
        response = requests.post(url, json=json, auth=authorisation)
        if response.status_code == 201:
            logger.info(f"... successful")
        else:
            logger.info(f"... failed, status={response.status_code}")
        index = index + 1


def create_batches():
    logger.info(f"creating batches of size {settings.BATCH_SIZE}")

    return list(chunks(to_batch, settings.BATCH_SIZE))


def ingest_folder(folder_entry):
    logger.info(f"ingesting folder {settings.PARENT_FOLDER}/{folder_entry.name}")

    entries = dbx.files_list_folder(f"{settings.PARENT_FOLDER}/{folder_entry.name}").entries

    with ThreadPoolExecutor(max_workers=settings.MAX_WORKERS) as executor:
        index = 1
        for item_entry in entries:
            executor.submit(ingest_item, folder_entry, item_entry, index)
            index = index + 1


def ingest_item(folder_entry, item_entry, index):
    logger.info(f"ingesting item {settings.PARENT_FOLDER}/{folder_entry.name}/{item_entry.name}")

    path_link_metadata = dbx.sharing_create_shared_link(path=f"{settings.PARENT_FOLDER}/{folder_entry.name}/{item_entry.name}", short_url=False, pending_upload=None)

    # logger.info(f"link metadata = {path_link_metadata.path} = {path_link_metadata.url}")

    shared_url = path_link_metadata.url.replace("dl=0", "dl=1")

    image = Image(id=f"{folder_entry.name}_{item_entry.name}", space=settings.DLCS_SPACE_ID, string_1=folder_entry.name, number_1=index, origin=shared_url)

    to_batch.append(image)


if __name__ == "__main__":
    if settings.DEBUG:
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    main()
