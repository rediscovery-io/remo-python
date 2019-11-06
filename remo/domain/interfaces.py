from abc import ABCMeta, abstractmethod


class ISDK(metaclass=ABCMeta):

    @abstractmethod
    def list_datasets(self) -> []:
        """
        :return: list of datasets
        """
        raise NotImplementedError

    @abstractmethod
    def list_annotation_sets(self, dataset_id):
        """
        :return: list of annotation sets for giving dataset
        """
        raise NotImplementedError
