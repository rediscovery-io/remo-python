from abc import ABCMeta, abstractmethod


class ISDK(metaclass=ABCMeta):

    @abstractmethod
    def datasets(self) -> []:
        """
        :return: list of datasets
        """
        raise NotImplementedError

    @abstractmethod
    def annotation_sets(self, dataset_id):
        """
        :return: list of annotation sets for giving dataset
        """
        raise NotImplementedError
