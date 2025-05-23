from typing import List, Dict, Optional, Callable # Added Callable
from ..core_models.sft_content_item import SFTContentItem
from ..core_models.client import Client, SexEnum 
from ..core_models.goal import Goal 

class StateManager:
    """
    Manages the state of the SFT framework, including parsed SFT content,
    client data, and goals.
    
    Initially, this will be an in-memory store. Later, it can be backed by a database.
    """
    def __init__(self):
        # SFT Content Storage
        self._sft_items_by_id: Dict[str, SFTContentItem] = {}
        self._sft_items_by_type: Dict[str, List[SFTContentItem]] = {}
        self._sft_item_children_map: Dict[str, List[SFTContentItem]] = {} 
        self._sft_items_by_source_file: Dict[str, List[SFTContentItem]] = {}

        # Client Data Storage
        self._clients_by_id: Dict[str, Client] = {}
        
        # Goal Data Storage
        self._goals_by_id: Dict[str, Goal] = {}
        self._goals_by_client_id: Dict[str, List[Goal]] = {}

    # --- SFT Content Item Methods ---
    def load_sft_items(self, items: List[SFTContentItem]):
        if not items: return
        # Clear previous items before loading new ones to prevent duplicates if called multiple times
        self.clear_sft_items_data()

        for item in items:
            if not isinstance(item, SFTContentItem):
                print(f"Warning: Attempted to load non-SFTContentItem: {type(item)}")
                continue
            
            self._sft_items_by_id[item.item_id] = item
            
            item_type_str = item.item_type 
            if item_type_str not in self._sft_items_by_type:
                self._sft_items_by_type[item_type_str] = []
            self._sft_items_by_type[item_type_str].append(item)
            
            if item.parent_item_id:
                if item.parent_item_id not in self._sft_item_children_map:
                    self._sft_item_children_map[item.parent_item_id] = []
                self._sft_item_children_map[item.parent_item_id].append(item)

            if item.source_file_path not in self._sft_items_by_source_file:
                self._sft_items_by_source_file[item.source_file_path] = []
            self._sft_items_by_source_file[item.source_file_path].append(item)
        
        for parent_id in self._sft_item_children_map:
            self._sft_item_children_map[parent_id].sort(
                key=lambda x: x.order_in_parent if x.order_in_parent is not None else float('inf')
            )
        print(f"StateManager: Loaded {len(self._sft_items_by_id)} unique SFTContentItems.")

    def get_sft_item_by_id(self, item_id: str) -> Optional[SFTContentItem]:
        return self._sft_items_by_id.get(item_id)

    def get_sft_items_by_type(self, item_type: str) -> List[SFTContentItem]:
        return self._sft_items_by_type.get(item_type, [])

    def get_children_of_item(self, parent_id: str) -> List[SFTContentItem]:
        return self._sft_item_children_map.get(parent_id, [])

    def get_sft_items_by_component_name(self, component_name: str, source_file_path_contains: Optional[str] = None) -> List[SFTContentItem]:
        """
        Retrieves SFTContentItems by component_name, optionally filtering by source_file_path.
        Returns a list as component_name might not be unique across all files.
        """
        results = []
        for item in self._sft_items_by_id.values():
            if hasattr(item, 'component_name') and item.component_name == component_name:
                if source_file_path_contains:
                    if source_file_path_contains in item.source_file_path:
                        results.append(item)
                else:
                    results.append(item)
        return results
    
    def get_sft_items(self, 
                      source_file_path: Optional[str] = None, 
                      item_type: Optional[str] = None, 
                      component_name: Optional[str] = None,
                      custom_filter: Optional[Callable[[SFTContentItem], bool]] = None
                      ) -> List[SFTContentItem]:
        """
        Generic method to retrieve SFTContentItems based on various criteria.
        Criteria are ANDed together.
        """
        candidate_items = list(self._sft_items_by_id.values())
        
        if source_file_path:
            candidate_items = [item for item in candidate_items if item.source_file_path == source_file_path]
        
        if item_type:
            candidate_items = [item for item in candidate_items if item.item_type == item_type]
            
        if component_name:
            candidate_items = [item for item in candidate_items if hasattr(item, 'component_name') and item.component_name == component_name]

        if custom_filter:
            candidate_items = [item for item in candidate_items if custom_filter(item)]
            
        return candidate_items

    def clear_sft_items_data(self):
        self._sft_items_by_id.clear()
        self._sft_items_by_type.clear()
        self._sft_item_children_map.clear()
        self._sft_items_by_source_file.clear()
        print("StateManager: All SFT content data cleared.")

    # --- Client Data Methods ---
    def add_client(self, client: Client):
        if not isinstance(client, Client):
            print(f"Warning: Attempted to add non-Client object: {type(client)}")
            return
        if client.client_id in self._clients_by_id:
            print(f"Warning: Client with ID {client.client_id} already exists. Updating.")
        self._clients_by_id[client.client_id] = client
        print(f"StateManager: Client '{client.full_name}' (ID: {client.client_id}) added/updated.")

    def get_client_by_id(self, client_id: str) -> Optional[Client]:
        return self._clients_by_id.get(client_id)

    def get_all_clients(self) -> List[Client]:
        return list(self._clients_by_id.values())

    def clear_client_data(self):
        self._clients_by_id.clear()
        print("StateManager: All client data cleared.")

    # --- Goal Data Methods ---
    def add_goal(self, goal: Goal):
        if not isinstance(goal, Goal):
            print(f"Warning: Attempted to add non-Goal object: {type(goal)}")
            return
        if goal.goal_id in self._goals_by_id:
            print(f"Warning: Goal with ID {goal.goal_id} already exists. Updating.")
        
        self._goals_by_id[goal.goal_id] = goal
        
        if goal.client_id not in self._goals_by_client_id:
            self._goals_by_client_id[goal.client_id] = []
        
        client_goals = self._goals_by_client_id[goal.client_id]
        existing_goal_idx = next((i for i, g in enumerate(client_goals) if g.goal_id == goal.goal_id), -1)
        if existing_goal_idx != -1:
            client_goals[existing_goal_idx] = goal 
        else:
            client_goals.append(goal)
            
        print(f"StateManager: Goal '{goal.overall_goal_summary[:30]}...' (ID: {goal.goal_id}) for client {goal.client_id} added/updated.")

    def get_goal_by_id(self, goal_id: str) -> Optional[Goal]:
        return self._goals_by_id.get(goal_id)

    def get_goals_by_client_id(self, client_id: str) -> List[Goal]:
        return self._goals_by_client_id.get(client_id, [])
    
    def get_active_goals_by_client_id(self, client_id: str) -> List[Goal]:
        client_goals = self._goals_by_client_id.get(client_id, [])
        return [goal for goal in client_goals if goal.is_active]

    def clear_goal_data(self):
        self._goals_by_id.clear()
        self._goals_by_client_id.clear()
        print("StateManager: All goal data cleared.")

    # --- Utility ---
    def clear_all_data(self):
        self.clear_sft_items_data()
        self.clear_client_data()
        self.clear_goal_data()
        print("StateManager: All data cleared.")
