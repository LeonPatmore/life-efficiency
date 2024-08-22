from dynamo.dynamo_repository import DynamoRepository
from finance.finance_manager import BalanceInstanceManager, BalanceInstance


class BalanceInstanceManagerDynamo(DynamoRepository, BalanceInstanceManager):

    def __init__(self):
        super(BalanceInstanceManagerDynamo, self).__init__(BalanceInstance)

    def add_instance(self, instance: BalanceInstance) -> BalanceInstance:
        return self.add(instance)

    def get_instances(self) -> list[BalanceInstance]:
        return self.get_all()
