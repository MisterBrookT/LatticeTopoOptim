import numpy as np
import subprocess
from ConfigSpace import Configuration, ConfigurationSpace, Float

from smac import BlackBoxFacade as BBFacade
from smac import RunHistory, Scenario



class TopoOptim:
    @property
    def configspace(self) -> ConfigurationSpace:
        
        # TODO: define the parameters: the diameter of outer and inner
        cs = ConfigurationSpace(seed=0)
        outer = Float("outer", (-5, 5), default=1)
        inner = Float("inner", (-10, 10), default=1)
        cs.add_hyperparameters([outer, inner])

        return cs
    
    
    # here we need to call abaqus for calculation and get the returned result
    def train(self, config: Configuration, seed: int = 0) -> float:
        
        outer = config["outer"]
        inner = config["inner"]

        # TODO： 执行abaqus命令, 这里只是1个example
        # command = ["abqus","cae","nogui=fcc.py" ,"--","0.3","0.5"]
        # result = subprocess.run(command, capture_output=True, text=True, shell=True)
        
        # TODO: 从目标obd拿到结果，odbfile会从odb文件中取出数据并写入output.txt：
        # command = ["abaqus","cae","nogui=odbfile.py","--","path of odb",]
        # result = subprocess.run(command, capture_output=True, text=True, shell=True)
        # x_test = None
        # max_ave_s = None
        # with open('output.txt', 'r') as file:
        #    for line in file:
        #        line = line.strip()
        #        if line.startswith("Max Ave E:"):
        #            x_test = float(line.split(":")[1].strip())
        #        elif line.startswith("Max Ave S:"):
        #            max_ave_s = float(line.split(":")[1].strip())
        # import os
        # os.remove('output.txt')
        
        return outer**2 + inner **2



if __name__ == "__main__":
    model = TopoOptim()

    # Scenario object specifying the optimization "environment"
    scenario = Scenario(model.configspace, deterministic=True, n_trials=100)

    # Now we use SMAC to find the best hyperparameters
    smac = BBFacade(
        scenario,
        model.train,  # We pass the target function here
        overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
    )

    incumbent = smac.optimize()

    # Get cost of default configuration
    default_cost = smac.validate(model.configspace.get_default_configuration())
    print(f"Default cost: {default_cost}")

    # Let's calculate the cost of the incumbent
    incumbent_cost = smac.validate(incumbent)
    print(f"Incumbent cost: {incumbent_cost}")

    # Let's plot it too
    # plot(smac.runhistory, incumbent)