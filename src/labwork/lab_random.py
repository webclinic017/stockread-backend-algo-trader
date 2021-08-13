# import random
#
# for _ in range(100):
#     rand = random.uniform(0, 1)
#     selected_rand = rand if rand < 0.85 else ''
#     print(rand, selected_rand)

# list1 = [1, 2, 3]
# list2 = [4, 5, 6]
# list2.append(list1.pop(1))
# print(list1)
# print(list2)
#
# # sth = 5
# # assert sth in list1
#
def simple_enum(operation_type: str = 'solar'):
    operation_types = {'update', 'insert', 'remove'}

    if operation_type not in operation_types:
        raise ValueError(f"InvalidOperationType: expected one of: {operation_types}")

#
#
# sim_func(1, 2, 3, sim_type='cu')

myorders = {'ord_1': '123', 'ord_2': '456'}
print(myorders.pop('ord_1'))


class Networkerror(RuntimeError):
   def __init__(self, arg):
      self.args = arg


# try:
#    raise Networkerror("Bad hostname")
# except Networkerror,e:
#    print e.args