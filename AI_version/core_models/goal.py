from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid # For generating unique goal_ids

class HealthScreeningModel(BaseModel):
    """
    Represents the health screening part of the SFT Goal Framework.
    """
    current_health_conditions: Optional[List[str]] = Field(default_factory=list)
    previous_injuries: Optional[List[str]] = Field(default_factory=list)
    ongoing_medical_treatments: Optional[List[str]] = Field(default_factory=list)
    physical_limitations: Optional[List[str]] = Field(default_factory=list)
    medical_clearance_status: Optional[str] = None # e.g., "Cleared", "Pending", "Not Cleared"
    current_medications: Optional[List[str]] = Field(default_factory=list)
    emergency_contact_information: Optional[str] = None # Could be a nested model later

class EntryFrameworkModel(BaseModel):
    """
    Represents the Entry Framework (المدخل) of the SFT Goal.
    """
    goal_definition: Optional[str] = None # ماذا تريد - What do you want?
    sensory_description: Optional[str] = None # الوصف الحسي - How will you know?
    purpose_identification: Optional[str] = None # لماذا - Why do you want it?

class ContextFrameworkModel(BaseModel):
    """
    Represents the Context Framework (السياق) of the SFT Goal.
    """
    temporal_planning: Optional[str] = None # متى - When?
    environmental_context: Optional[str] = None # أين - Where?
    support_network: Optional[str] = None # مع من - With Whom?

class ImplementationFrameworkModel(BaseModel):
    """
    Represents the Implementation Framework (الكيفية - How) of the SFT Goal.
    """
    required_actions: Optional[str] = None # كيف ستحقق هدفك - How will you achieve it?
    self_verification: Optional[str] = None # كيف تتأكد من نفسك - How will you verify yourself?
    resource_allocation: Optional[str] = None # الموارد المطلوبة - Required Resources
    progress_metrics: Optional[str] = None # مقاييس التقدم - Progress Measurements
    obstacle_management: Optional[str] = None # إدارة العقبات - Managing Obstacles
    integration_strategy: Optional[str] = None # استراتيجية التكامل - Integration Strategy
    performance_enhancement: Optional[str] = None # تحسين الأداء - Performance Enhancement
    system_protection: Optional[str] = None # حماية النظام - System Protection
    development_tracking: Optional[str] = None # تتبع التطور - Progress Tracking

class VerificationFrameworkModel(BaseModel):
    """
    Represents the Verification Framework (التأكد) of the SFT Goal.
    """
    balance_assessment: Optional[str] = None # التوازن
    commitment_level: Optional[str] = None # القرار (e.g., a rating or textual description)
    achievement_verification_summary: Optional[str] = None # التحقق من الإنجاز

class Goal(BaseModel):
    """
    Represents a client's goal within the SFT system, structured
    according to the Unified Goal Framework.
    """
    goal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str # Links to the Client model's client_id
    overall_goal_summary: str # A concise summary of the main goal
    
    sft_level_target: Optional[int] = None # e.g., aiming for SFT Level 1, 2, or 3
    is_active: bool = True
    
    creation_date: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow) # Should be updated on modification

    # Nested models for each framework stage
    health_screening: Optional[HealthScreeningModel] = Field(default_factory=HealthScreeningModel)
    entry_framework: Optional[EntryFrameworkModel] = Field(default_factory=EntryFrameworkModel)
    context_framework: Optional[ContextFrameworkModel] = Field(default_factory=ContextFrameworkModel)
    implementation_framework: Optional[ImplementationFrameworkModel] = Field(default_factory=ImplementationFrameworkModel)
    verification_framework: Optional[VerificationFrameworkModel] = Field(default_factory=VerificationFrameworkModel)

    class Config:
        use_enum_values = True # If enums were used directly in this model
        validate_assignment = True # To re-validate on field assignment

    def mark_updated(self):
        self.last_updated = datetime.utcnow()

# Example Usage (for testing or understanding):
# if __name__ == "__main__":
#     goal_data = {
#         "client_id": "client_123",
#         "overall_goal_summary": "Achieve SFT Level 1 focusing on functional strength and mobility.",
#         "sft_level_target": 1,
#         "entry_framework": {
#             "goal_definition": "Master foundational movement patterns and build consistent training habits.",
#             "sensory_description": "Will be able to perform 10 perfect push-ups, hold a 60s plank, and feel more energetic.",
#             "purpose_identification": "To improve overall health, build a strong base for future training, and feel more capable."
#         }
#     }
#     new_goal = Goal(**goal_data)
#     print(new_goal.model_dump_json(indent=2))
#     new_goal.mark_updated()
#     print(f"Goal ID: {new_goal.goal_id}")
#     print(f"Last Updated: {new_goal.last_updated}")
#     if new_goal.health_screening:
#         new_goal.health_screening.current_health_conditions = ["Mild knee pain"]
#     print(new_goal.model_dump_json(indent=2))
