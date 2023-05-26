import gym
import inspect
import rlproject

env = gym.make('rlproject/RLproject-v0')
# env.step()
# env.reset()

env.seed(42)

# Get the instance attributes and their shapes/types
instance_attributes = env.__dict__

for attr_name, attr_value in instance_attributes.items():
    print(f"Instance Attribute: {attr_name}")
    if hasattr(attr_value, "shape"):
        print(f"Value: {attr_value}")
        print(f"Shape: {attr_value.shape}")
    print(f"Type: {type(attr_value)}")
    print()

# Get class variables (attributes)
class_variables = env.__class__.__dict__
for variable_name, variable_value in class_variables.items():
    if not inspect.isroutine(variable_value):  # Check if it's not a function
        print(f"Variable Name: {variable_name}")
        print(f"Variable Value: {variable_value}")
        print(f"Type: {type(variable_value)}")
        print(f"Shape: {getattr(variable_value, 'shape', None)}")
        print()

# Get class functions (methods)
class_functions = inspect.getmembers(env, predicate=inspect.ismethod)
for function_name, function_object in class_functions:
    print(f"Function Name: {function_name}")
    print(f"Function Code:")
    print(inspect.getsource(function_object))
    print()
