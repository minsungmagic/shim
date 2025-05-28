class Inventory:
    def __init__(self, env, factory, resource, s, S, restock_time):
        self.env = env
        self.factory = factory
        self.resource = resource
        self.s = s
        self.S = S
        self.restock_time = restock_time
        self.env.process(self.monitor_inventory())

    def monitor_inventory(self):
        while True:
            if self.resource.level <= self.s:
                amount_to_restock = self.S - self.resource.level
                print(f"{self.env.now:.2f}: {self.resource.name} 재고 {self.resource.level:.2f}, 보충 {amount_to_restock:.2f}")
                yield self.env.timeout(self.restock_time)
                yield self.resource.put(amount_to_restock)
            yield self.env.timeout(1)