# -*- coding: utf-8 -*-
"""
Load datasets for models
@author: jpeeples
"""

## Python standard libraries
from __future__ import print_function
from __future__ import division

## PyTorch dependencies
import torch

## Local external libraries
from Utils.Get_min_max import get_min_max_minibatch
from Utils.Get_min_max_zero import get_min_max_minibatch_zero
from Utils.Get_standarize import get_standardization_minibatch
from Datasets.DeepShipSegments import DeepShipSegments
from Datasets.Get_preprocessed_data import process_data


def Prepare_DataLoaders(Network_parameters):
    
    Dataset = Network_parameters['Dataset']
    data_dir = Network_parameters['data_dir']
    process_data(sample_rate=Network_parameters['sample_rate'], segment_length=Network_parameters['segment_length'])

    
    #Change input to network based on models
    #If TDNN or HLTDNN, number of input features is 1
    #Else (CNN), replicate input to be 3 channels
    #If number of input channels is 3 for TDNN, RGB will be set to False
    if (Network_parameters['Model_name'] == 'TDNN' and Network_parameters['TDNN_feats'][Dataset]):
        RGB = False
    else:
        RGB = True
        
    if Dataset == 'DeepShip':
        train_dataset = DeepShipSegments(data_dir, partition='train')
        val_dataset = DeepShipSegments(data_dir, partition='val')
        test_dataset = DeepShipSegments(data_dir, partition='test')        
    else:
        raise RuntimeError('Dataset not implemented') 

    #Compute min max norm of training data for normalization
    norm_function = get_min_max_minibatch(train_dataset, batch_size=128)
    
    #Set normalization function for each dataset
    train_dataset.norm_function = norm_function
    val_dataset.norm_function = norm_function
    test_dataset.norm_function = norm_function

    #Create dictionary of datasets
    image_datasets = {'train': train_dataset, 'val': val_dataset, 'test': test_dataset}
    
    # Create training and test dataloaders
    dataloaders_dict = {x: torch.utils.data.DataLoader(image_datasets[x],
                                                       batch_size=Network_parameters['batch_size'][x],
                                                       shuffle=True,
                                                       num_workers=Network_parameters['num_workers'],
                                                       pin_memory=Network_parameters['pin_memory'])
                                                       for x in ['train', 'val','test']}

    return dataloaders_dict
    

