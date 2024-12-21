from pathlib import Path

import fire
from loguru import logger
from natsort import natsorted

from mokuro import OverlayGenerator
from mokuro.utils import get_supported_file_types, path_is_supported_input, unzip_if_zipped

def run(*paths,
        parent_dir=None,
        pretrained_model_name_or_path='kha-white/manga-ocr-base',
        force_cpu=False,
        as_one_file=True,
        disable_confirmation=False,
        disable_ocr=False,
        ):
    
    if disable_ocr:
        logger.info('Running with OCR disabled')

    paths = [Path(p).expanduser().absolute() for p in paths]

    if parent_dir is not None:
        for p in Path(parent_dir).expanduser().absolute().iterdir():
            if path_is_supported_input(p) and p.stem != '_ocr' and p not in paths:
                if p.is_dir() or not p.with_suffix("").exists():
                    paths.append(p)
                else:
                    logger.warning(f"Skipping path '{p}' due to matching directory of same name.")

    if len(paths) == 0:
        logger.error('Found no paths to process. Did you set the paths correctly?')
        return

    paths = natsorted(paths)

    print(f'\nPaths to process:\n')
    for p in paths:
        print(p)

    if not disable_confirmation:
        inp = input('\nEach of the paths above will be treated as one volume. Continue? [yes/no]\n')
        if inp.lower() not in ('y', 'yes'):
            return

    ovg = OverlayGenerator(pretrained_model_name_or_path=pretrained_model_name_or_path, force_cpu=force_cpu, disable_ocr=disable_ocr)

    num_successful = 0
    for i, path in enumerate(paths):
        logger.info(f'Processing {i + 1}/{len(paths)}: {path}')
        if not path_is_supported_input(path):
            logger.exception(f'Error while processing {path}.\nPath must be a directory or a supported file type: {(", ").join(get_supported_file_types())}.')
        try:
            content_path = unzip_if_zipped(path)
        except Exception as e:
            logger.exception(f'Error while processing {path}')
        else:
            num_successful += 1

    logger.info(f'Processed successfully: {num_successful}/{len(paths)}')


if __name__ == '__main__':
    fire.Fire(run)
