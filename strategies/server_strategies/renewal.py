from strategies.server_strategies.server_strategy import ServerStrategy

class RenewalStrategy(ServerStrategy):

    def age_density(self, z, args):
        raise NotImplementedError("Age density not defined for renewal strategy")

    def age_distribution(self, z, args):
        raise NotImplementedError("Age distribution not defined for renewal strategy")
