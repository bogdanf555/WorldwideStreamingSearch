import sys
import json
from os import path, makedirs

from justwatch import JustWatch
import pycountry

providers = ['nfx', 'hbm', 'dnp', 'sst', 'prv', 'mbi']
providers_fullname = {
    "nfx": "Netflix",
    "hbm": "HBO Max",
    "dnp": "Disney+",
    "sst": "SkyShowtime",
    "prv": "Prime Video",
    "mbi": "Mubi"
}
preffered_countries = ['RO', 'US', 'GB']
countries = ['AL', 'AG', 'AR', 'AU', 'AT', 'BS', 'BB', 'BE', 'BO', 'BA', 'BR', 'BG', 'CA', 
             'CV', 'CL', 'CO', 'CR', 'HR', 'CZ', 'DK', 'DO', 'EC', 'EG', 'SV', 'EE', 'FJ', 
             'FI', 'FR', 'GF', 'DE', 'GR', 'GT', 'HN', 'HK', 'HU', 'IS', 'IN', 'ID', 'IE', 
             'IL', 'IT', 'CI', 'JM', 'JP', 'LV', 'LT', 'MK', 'MY', 'MT', 'MU', 'MX', 'MD', 
             'MZ', 'NL', 'NZ', 'NE', 'NO', 'PA', 'PY', 'PE', 'PH', 'PL', 'PT', 'RO', 'RU', 
             'SA', 'SN', 'RS', 'SG', 'SK', 'SI', 'ZA', 'KR', 'ES', 'SE', 'CH', 'TW', 'TH', 
             'TT', 'TR', 'UG', 'AE', 'GB', 'US', 'UY', 'VE', 'ZM']

def print_json(object: dict):
    print(json.dumps(object, indent=2, default=str))

def write_json(object: dict, filename):
    with open(filename, 'w') as file:
        file.write(json.dumps(object, indent=2, default=str))

def fetch_id_from_us(title: str):
    us_watcher = JustWatch(country='US')
    return us_watcher.search_for_item(title)['items'][0]['id']

def search_in_countries(title, id):

    watcher = JustWatch(providers=providers)

    final_results = {
        'title': title,
        'preffered': [],
        'others': []
    }

    for country in countries:
        
        # set the country
        watcher.country = country
        watcher.locale = watcher.set_locale()

        # query db
        results = watcher.search_for_item(title)

        # find the result specific for this title's id
        searched_for = None
        for result in results['items']:
            if id == result['id']:
                searched_for = result
                break

        # if the id not found in results just skip this country
        if searched_for is None or not searched_for['offers']:
            continue

        # filter by our providers
        offers = list(filter(lambda offer: offer['package_short_name'] in providers, searched_for['offers']))
    
        # availability
        available_on = set()
        for offer in offers:
            available_on.add(providers_fullname[offer['package_short_name']])
        available_on = list(available_on) if len(available_on) > 1 else next(iter(available_on))

        # register this result to final results
        result = {'country': pycountry.countries.get(alpha_2=country).name, 'available_on': available_on}
    
        if country in preffered_countries:
            final_results['preffered'].append(result)
        else:
            final_results['others'].append(result)
    
    if not path.isdir('results'):
        makedirs('results')

    write_json(final_results, path.join('results', title.replace(" ", '_').replace(":", "") + '.json'))

def main():
    title = sys.argv[1]
    id = fetch_id_from_us(title)
    search_in_countries(title, id)


if __name__ == '__main__':
    main()