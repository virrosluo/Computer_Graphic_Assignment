import copy

class NestedObject:
    def __init__(self, nested_value):
        self.nested_value = nested_value

    def __repr__(self):
        return f"NestedObject(nested_value={self.nested_value})"

class MyObject:
    def __init__(self, value, nested_obj):
        self.value = value
        self.nested_obj = nested_obj  # This is an instance of NestedObject

    def __repr__(self):
        return f"MyObject(value={self.value}, nested_obj={self.nested_obj})"

# Create a list of MyObject instances, each containing a NestedObject
nested1 = NestedObject(100)
nested2 = NestedObject(200)
original_list = [MyObject(1, nested1), MyObject(2, nested2)]

# Deep copy the list
copied_list = copy.deepcopy(original_list)

# Modify the original list to demonstrate deep copy behavior
original_list[0].value = 10
original_list[0].nested_obj.nested_value = 999

print("Original list:", original_list)
print("Copied list:", copied_list)
