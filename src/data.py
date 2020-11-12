import torch
import datasets
from config import cfg
from torch.utils.data import Dataset, DataLoader
from torch.utils.data.dataloader import default_collate


def fetch_dataset(data_name, subset, verbose=True):
    dataset = {}
    if verbose:
        print('fetching data {}...'.format(data_name))
    root = './data/{}'.format(data_name)
    if data_name in ['Blob', 'QSAR', 'Wine']:
        dataset['train'] = eval('datasets.{}(root=root, split=\'train\', subset=subset)'.format(data_name))
        dataset['test'] = eval('datasets.{}(root=root, split=\'test\', subset=subset)'.format(data_name))
    else:
        raise ValueError('Not valid dataset name')
    if verbose:
        print('data ready')
    return dataset


def input_collate(batch):
    if isinstance(batch[0], dict):
        output = {key: [] for key in batch[0].keys()}
        for b in batch:
            for key in b:
                output[key].append(b[key])
        return output
    else:
        return default_collate(batch)


def make_data_loader(dataset, tag):
    data_loader = {}
    for k in dataset:
        data_loader[k] = DataLoader(dataset=dataset[k], shuffle=cfg[tag]['shuffle'][k],
                                    batch_size=cfg[tag]['batch_size'][k],
                                    pin_memory=True, num_workers=cfg['num_workers'], collate_fn=input_collate)
    return data_loader


def split_dataset(num_users):
    if cfg['data_name'] in ['Blob', 'QSAR', 'Wine']:
        num_features = cfg['data_shape'][0]
        feature_split = list(torch.randperm(num_features).split(num_features // num_users))
        feature_split = feature_split[:num_users - 1] + [torch.cat(feature_split[num_users - 1:])]
    else:
        raise ValueError('Not valid data name')
    return feature_split