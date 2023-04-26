import torch as th
from torch import nn
from torch.utils.data import Dataset, DataLoader

"""
Author: Josue N Rivera
"""

class Company():

    def __init__(self, name:str, 
                 dataset:Dataset, 
                 distribution:th.Tensor, 
                 model:nn.Module, 
                 epochs:int = 5, 
                 batch_size = 100,
                 opt = th.optim.Adam,
                 criterion = th.nn.CrossEntropyLoss) -> None:
        self.name = name
        self.dataset = dataset
        self.distribution = distribution
        self.partners = None
        self.partners_request_API = []
        self.model = model
        self.epochs = epochs
        self.batch_size = batch_size
        self.dataloader = DataLoader(self.dataset, self.batch_size, shuffle=True, num_workers=3)
        self.opt = opt(self.model.parameters())
        self.criterion = criterion()

    def set_partners(self, partners, partners_request_API) -> None:
        self.partners = partners
        self.partners_request_API = partners_request_API

    def train(self):
        device = th.device("cuda:0" if th.cuda.is_available() else "cpu")

        for epoch in range(self.epochs):
            for imgs, labels in self.dataloader:
                self.opt.zero_grad()
                output = self.model(imgs).to(device)
                loss = self.criterion(output, labels)

                loss.backward()
                self.opt.step()

    def merge_parameters(self):

        self.my_parameters = self.request_parameters()

        partners_parameters = {}
        for key in self.my_parameters:
            partners_parameters[key] = []

        for request_parameter in self.partners_request_API:
            partner_parameters = request_parameter()

            for key in self.my_parameters:
                partners_parameters[key].append(partner_parameters[key])
        
        for key in self.my_parameters:
            partners_parameters = sum(partners_parameters[key]) / float(len(self.partners))
            self.my_parameters[key] = (self.my_parameters[key] + partners_parameters[key]) / 2.

    def request_parameters(self):
        return self.model.state_dict()

    def update_parameters(self):
        self.model.load_state_dict(self.my_parameters)

    def validate(self, dataset:Dataset):
        pass

    