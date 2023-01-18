from typing import Callable, List, Tuple, Union
from types import FrameType, FunctionType
from treelib import Tree, Node
from treelib import exceptions as treelib_exceptions
import sys

def find_tracked_parent(func_names_to_track, parent_frame:FrameType) -> Union[FrameType, None]:
    if parent_frame.f_code.co_name in func_names_to_track:
        return parent_frame
    
    if parent_frame.f_back == None:
        return None
    
    return find_tracked_parent(func_names_to_track, parent_frame.f_back)

def make_recursion_tracker(funcs_to_track:List[Callable]) -> Tuple[Callable, Callable[[],Tree]]:
    recursion_tree = Tree()
    root_node = Node()
    recursion_tree.add_node(root_node)

    func_names_to_track = list(map(lambda func: func.__name__ ,funcs_to_track))
    def track_recursion(frame: FrameType, event, arg):
        if event != 'call':
            return
        func_name = frame.f_back.f_code.co_name
        if func_name not in func_names_to_track:
            # print(func_name)
            # print(list(func_names_to_track))
            return

        # find parent that is being tracked
        tracked_parent = find_tracked_parent(func_names_to_track, frame)

        # link nodes
        tracked_parent_node = None
        if tracked_parent is None:
            tracked_parent_node = root_node
        else:
            tracked_parent_node = recursion_tree.get_node(tracked_parent.__hash__())
            if tracked_parent_node == None:
                print("Failed to find parent")
                return
        recursion_tree.add_node(Node(identifier=frame.__hash__()),parent=tracked_parent_node)
        
        current_node: Node = recursion_tree.get_node(frame.__hash__)
        # set tag to func name
        current_node.tag = func_name

        # set data to call arguments
        args = {}
        for arg_name in frame.f_code.co_varnames:
            args[arg_name] = frame.f_locals[arg_name]
        current_node.data = args

    def get_recursion_tree():
        return recursion_tree   
    return track_recursion, get_recursion_tree
