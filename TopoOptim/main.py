import numpy as np
import subprocess
from ConfigSpace import Configuration, ConfigurationSpace, Float

from smac import BlackBoxFacade as BBFacade
from smac import RunHistory, Scenario



class TopoOptim:
    call_abaqus = 0

    @property
    def configspace(self) -> ConfigurationSpace:
        
        # TODO: define the parameters: the diameter of outer and inner
        cs = ConfigurationSpace(seed=0)
        outer = Float("outer", (0.5, 0.8), default=0.6)
        inner = Float("inner", (0.1, 0.4), default=0.2)
        cs.add_hyperparameters([outer, inner])

        return cs
    
    
    # here we need to call abaqus for calculation and get the returned result
    def train(self, config: Configuration, seed: int = 0) -> float:
        
        TopoOptim.call_abaqus += 1
        print(TopoOptim.call_abaqus)
        outer = round(config["outer"], 3)
        inner = round(config["inner"], 3)
        path_odb = f"{TopoOptim.call_abaqus}.odb"
        # # 执行abaqus命令
        command = f"abq cae nogui=fcc_job_commit.py -- {inner} {outer} {path_odb} 0"
        print(command)

        result = subprocess.run(command,  text=True, shell=True)
        # # 执行后处理
        command = f"abq cae nogui=fcc_postprocess.py -- {path_odb}"
        result = subprocess.run(command, text=True, shell=True)
        x_test = None
        max_ave_s = None
        with open('output.txt', 'r') as file:
           for line in file:
               line = line.strip()
               if line.startswith("Max Ave E:"):
                   x_test = float(line.split(":")[1].strip())
               elif line.startswith("Max Ave S:"):
                   max_ave_s = float(line.split(":")[1].strip())

        if max_ave_s is None:
            raise ValueError("max_ave_s should not be [None]")
        return 1-max_ave_s
        # return max_ave_s

    # TODO: Maybe we need to use a simple example for running before we really run fcc lattice.
    def test() -> None:
        pass



if __name__ == "__main__":
    model = TopoOptim()
    
    # Scenario object specifying the optimization "environment"
    scenario = Scenario(model.configspace, deterministic=True, n_trials=20)

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