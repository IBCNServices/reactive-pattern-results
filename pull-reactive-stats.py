#!/usr/bin/env python3
import os
import json
import operator
from collections import defaultdict

import yaml
import requests

API_URL = "https://api.jujucharms.com/charmstore/v5"

def filename(charmname, type):
    return "cached/{}/{}.json".format(type, charmname.replace('/',':'))


def cache_charm_list():
    resp = requests.get(API_URL + '/list?type=charm&series=xenial')
    charms = resp.json()['Results']
    with open('cached/charm-list-cached.json', 'w') as f:
        json.dump(charms, f, indent=4)


def get_charms():
    with open('cached/charm-list-cached.json', 'r') as f:
        charms = json.load(f)
    return [charm['Id'][3:] for charm in charms]


def get_reactive_charms():
    reactive_charms = []
    for name in get_charms():
        if os.path.isfile(filename(name, 'layer-yaml')):
            reactive_charms.append(name)
    return reactive_charms


def cache_layer_files():
    charms = get_charms()
    numreactive = 0
    for name in charms:
        resp = requests.get("{}/{}/archive/layer.yaml".format(API_URL, name))
        if resp.status_code == 200:
            numreactive += 1
            layer = yaml.load(resp.text)
            with open(filename(name, 'layer-yaml'), 'w') as f:
                json.dump(layer, f, indent=4)
    print("Total charms: {}\nReactive charms: {}".format(len(charms), numreactive))


def get_layer_yaml(name):
    path = filename(name, 'layer-yaml')
    try:
        with open(path, 'r') as f:
            layer_yaml = json.load(f)
            return layer_yaml
    except:
        return None


def normalize(name):
    name = name.split('/')[-1]
    import re
    name = re.sub('(-[0-9]+$)', '', name)
    return name

def get_normalized_deps():
    deps = defaultdict(set)
    for name in get_reactive_charms():
        n_name = normalize(name)
        layer_yaml = get_layer_yaml(name)
        deps[n_name].update(set(layer_yaml.get('includes', [])))
    return deps

cache_charm_list()
cache_layer_files()

# print("WOL: " + str(get_reactive_charms()))
# print(filename("WOL", 'layer-yaml'))


# charms = get_reactive_charms()
# print(filename(charms[0], 'layer-yaml'))



# layers = defaultdict(list)
# interfaces = defaultdict(list)

# print("NUMBER OF REACTIVE CHARMS: {}".format(len(get_reactive_charms())))

def get_deps():
    layers = defaultdict(list)
    interfaces = defaultdict(list)

    deps = get_normalized_deps()

    for name in deps:
        for incl in list(deps[name]):
            type, l_name = incl.split(':')
            if type in ('layer', 'cs'):
                layers[l_name].append(name)
            elif type == 'interface':
                interfaces[l_name].append(name)
            else:
                print("type {} not known".format(type))
    return (layers, interfaces)


layers, interfaces = get_deps()

sorted_layers = sorted(layers.items(), key=lambda itempair: len(itempair[1]), reverse=True)
sorted_interfaces = sorted(interfaces.items(), key=lambda itempair: len(itempair[1]), reverse=True)

l_counts = {name: len(layers[name]) for name in layers}
i_counts = {name: len(interfaces[name]) for name in interfaces}
sorted_l_counts = sorted(l_counts.items(), key=operator.itemgetter(1), reverse=True)
sorted_i_counts = sorted(i_counts.items(), key=operator.itemgetter(1), reverse=True)


with open('cached/layer-usage-raw', 'w') as f:
    json.dump(sorted_layers, f, indent=4)
with open('cached/interface-usage-raw', 'w') as f:
    json.dump(sorted_interfaces, f, indent=4)

with open('cached/layer-usage', 'w') as f:
    json.dump(sorted_l_counts, f, indent=4)
with open('cached/interface-usage', 'w') as f:
    json.dump(sorted_i_counts, f, indent=4)

print("Total reactive charms (normalized): {}".format(len(get_normalized_deps())))

print("LAYERS")
for layer in sorted_l_counts[:10]:
    print("{}: {}".format(layer[0], layer[1]))
print()
print("INTERFACES")
for interface in sorted_i_counts[:10]:
    print("{}: {}".format(interface[0], interface[1]))

# print(sorted_l_counts)
# print()
# print()

# print(sorted_i_counts)