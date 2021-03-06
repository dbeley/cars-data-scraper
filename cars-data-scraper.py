import time
import logging
import argparse
import requests
import os
from bs4 import BeautifulSoup
import pandas as pd
from itertools import zip_longest


logger = logging.getLogger()
temps_debut = time.time()


def get_soup(url):
    return BeautifulSoup(requests.get(url).content, features='lxml')


def get_brands(url):
    brands = []
    soup = get_soup(url)
    for brand in soup.find_all('div', {'class': 'col-2 center'}):
        brands.append(str(brand.find('a')['href']))
    soup.decompose()
    return brands


def get_models(url):
    models = []
    soup = get_soup(url)
    for model in soup.find_all('div', {'class': 'col-4'}):
        try:
            models.append(str(model.find('a')['href']))
        except Exception:
            pass
    soup.decompose()
    return models


def get_versions(url):
    versions = []
    soup = get_soup(url)
    for version in soup.find_all('div', {'class': 'col-4'}):
        try:
            versions.append(str(version.find('a')['href']))
        except Exception:
            pass
    soup.decompose()
    return versions


def get_motors(url):
    motors = []
    soup = get_soup(url)
    for motor in soup.find_all('div', {'class': 'col-6'}):
        try:
            motors.append(str(motor.find('a')['href']))
        except Exception:
            pass
    soup.decompose()
    return motors


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def get_specs(url):
    dict = {}
    soup = get_soup(url)
    main_specs = soup.find('div', {'id': 'breadcrumb'}).find_all('a')
    dict["Brand"] = str(main_specs[1].find('span').find(text=True))
    dict["Model"] = str(main_specs[2].find('span').find(text=True))
    dict["Version"] = str(main_specs[3].find('span').find(text=True))
    dict["Motor"] = str(main_specs[4].find('span').find(text=True))
    print(f"Extracting {dict['Motor']}")
    detailed_specs = soup.find_all(True, {'class': 'col-6'})
    for a, b in grouper(detailed_specs, 2):
        try:
            type = str(a.find(text=True).replace(":", ""))
            value = str(b.find(text=True))
            dict[type] = value
        except Exception:
            pass
    soup.decompose()
    return dict


def main():
    args = parse_args()

    url_index = "https://www.cars-data.com/en/car-brands-cars-logos.html"
    cars_dict = dict()
    index_dict = 0
    cars_brands = get_brands(url_index)

    # logger.debug(f"Brands : {cars_brands}")

    directory = "Exports"
    if not os.path.exists(directory):
        logger.debug("Creating Exports Folder")
        os.makedirs(directory)

    for brand in cars_brands:
        already_made = []
        already_made = [f"https://www.cars-data.com/en/{x}" for x in already_made]
        if brand and brand not in already_made:
            print(f"Brand : {brand}")
            models = get_models(brand)
            # logger.debug(f"Models : {models}")
            for model in models:
                if model:
                    logger.debug(f"Model : {model}")
                    versions = get_versions(model)
                    # logger.debug(f"Versions : {versions}")
                    for version in versions:
                        if version:
                            logger.debug(f"Version : {version}")
                            motors = get_motors(version)
                            # logger.debug(f"Motors : {motors}")
                            for motor in motors:
                                if motor:
                                    logger.debug(f"Motor : {motor}")
                                    dict_specs = get_specs(motor)
                                    cars_dict[index_dict] = dict_specs
                                    index_dict = index_dict + 1
                                    time.sleep(1)
                                    # break
            df = pd.DataFrame.from_dict(cars_dict, orient='index')
            try:
                filename = f"{directory}/cars_{cars_dict[0]['Brand']}.csv"
                print(f"Writing {filename}")
                df.to_csv(filename, sep=";")
            except Exception as e:
                logger.error(f"Error exporting brand {brand} : {str(e)}")
            cars_dict = dict()
            index_dict = 0

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper cars-data.')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
