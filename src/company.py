from typing import Any, Dict
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
                 shared_model:nn.Module,
                 device = th.device("cuda:0" if th.cuda.is_available() else "cpu"),
                 epochs:int = 5, 
                 batch_size = 50,
                 opt = th.optim.SGD,
                 criterion = th.nn.CrossEntropyLoss) -> None:
        self.name = name
        self.dataset = dataset
        self.distribution = distribution
        self.partners = []
        self.partners_request_API = []
        self.device = device
        self.model = shared_model
        self.epochs = epochs
        self.batch_size = batch_size
        self.dataloader = DataLoader(self.dataset, self.batch_size, shuffle=True, num_workers=3)
        self.opt = opt(self.model.parameters(), lr=0.001)
        self.criterion = criterion()

    def __str__(self) -> str:

        return f"{self.name}:\n \
                 Distribution (%) = {th.round(self.distribution*100).to(th.int).tolist()}\n\
                 Neighbors = {[i+1 for i in self.partners]}"

    def set_partners(self, partners:list, partners_request_API:list) -> None:
        self.partners = partners
        self.partners_request_API = partners_request_API

    def train(self):
        self.model.train()

        for _ in range(self.epochs):
            for __, ld in enumerate(self.dataloader):
                data, targets = ld

                data, targets = data.to(self.device), targets.to(self.device)
                self.opt.zero_grad()
                output = self.model(data.to(self.device))
                loss = self.criterion(output, targets.to(self.device))

                loss.backward()
                self.opt.step()

    def merge_parameters(self) -> None:

        self.my_parameters = self.request_parameters()

        if len(self.partners) <= 0:
            return

        partners_parameters = {}
        for key in self.my_parameters:
            partners_parameters[key] = []

        for request_parameter in self.partners_request_API:
            partner_parameters = request_parameter()

            for key in self.my_parameters:
                partners_parameters[key].append(partner_parameters[key])
        
        for key in self.my_parameters:
            par2avg = sum(partners_parameters[key]) / float(len(self.partners))
            self.my_parameters[key] = (self.my_parameters[key] + par2avg) / 2

    def request_parameters(self) -> Dict[str, Any]:
        return self.model.state_dict()

    def update_parameters(self):
        self.model.load_state_dict(self.my_parameters)

    def validate(self, test_loader:DataLoader):
        self.model.eval()
        test_loss = 0
        correct = 0

        with th.no_grad():
            for _, ld in enumerate(test_loader):
                data, targets = ld

                data, targets = data.to(self.device), targets.to(self.device)
                output = self.model(data)
                test_loss += self.criterion(output, targets).item()  # sum up batch loss
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(targets.view_as(pred)).sum().item()

        test_loss /= len(test_loader.dataset)

        return test_loss

    