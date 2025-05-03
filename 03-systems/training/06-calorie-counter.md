<!-- AI.FRAMEWORK.COMPONENT: NUTRITION_CALORIE_COUNTER -->
<!-- AI.METADATA
component: nutrition_calorie_counter
version: 1.1
last_updated: 03/05/2025
framework_type: implementation_system
language: en-US
parent: superfunctional_training_system
path: 03-systems/training/06-calorie-counter
references: master_mission,unified_goal_framework,nutrition_implementation,energy_systems
-->

# CALORIE COUNTER TOOL

## CORE FUNCTIONALITY

<!-- AI.CONTEXT: CORE_FUNCTIONALITY -->

### Food Database Integration

**Implementation:**
1. Dynamic regional database
   - Automatic region detection
   - Location-based food prioritization
   - Region-specific portion standards
   - Local terminology recognition
   - Cultural food combinations

2. Custom food addition
   - Natural language input processing
   - Multiple format handling
   - Portion customization
   - Favorites storage

### Calculation Tools

**Implementation:**
1. Daily intake calculator
   - Individual food tracking
   - Complete meal logging
   - Running total maintenance
   - Remaining calorie/macro display
   - Progress percentage indicators

2. Weekly overview
   - Pattern analysis
   - Average calculations
   - Goal alignment
   - Recommendation generation
<!-- AI.CONTEXT.END: CORE_FUNCTIONALITY -->

## USER INTERACTION

<!-- AI.CONTEXT: USER_INTERACTION -->

### Input Methods

**Implementation:**
1. Direct text entry
   - Natural language processing
   - Multiple language support (region-specific)
   - Unit conversion handling (regional measurements)
   - Mixed format parsing

2. List format
   - Line-by-line entry
   - Multiple item processing
   - Automatic categorization
   - Quantity recognition

### Output Formats

**Implementation:**
1. Structured list
   - Individual item breakdown
   - Per-item macronutrient display
   - Meal totals calculation
   - Daily remaining statistics

2. Format elements
   - Emoji integration (🍽️,⚡,📊)
   - Visual organization
   - Percentage indicators
   - Personalized recommendations
<!-- AI.CONTEXT.END: USER_INTERACTION -->

## DISPLAY TEMPLATES

<!-- AI.CONTEXT: DISPLAY_TEMPLATES -->

### Standard Meal Display

**Format:**
```
**🍽️ MEAL LOGGED:**
- [food item]: 
  [calories] kcal
  (P: [protein]g | C: [carbs]g | F: [fat]g)

- [food item]: 
  [calories] kcal
  (P: [protein]g | C: [carbs]g | F: [fat]g)

- **TOTAL**: 
  [total calories] kcal
  (P: [total protein]g | C: [total carbs]g | F: [total fat]g)

**⚡ REMAINING TODAY:**
- Calories: [remaining] / [goal] ([percentage]%)
- Protein: [remaining]g / [goal]g ([percentage]%)
- Carbs: [remaining]g / [goal]g ([percentage]%)
- Fat: [remaining]g / [goal]g ([percentage]%)

**📊 SUMMARY:** [personalized recommendation based on meal analysis]
```

### Quick Format

**Compact Display:**
```
📊 **MEAL**: [food items] = [total calories] kcal (P: [protein]g | C: [carbs]g | F: [fat]g)
⚡ **REMAINING**: [remaining calories] kcal | [remaining protein]g protein | [remaining carbs]g carbs | [remaining fat]g fat
```
<!-- AI.CONTEXT.END: DISPLAY_TEMPLATES -->

## REGIONAL FOOD DATABASE

<!-- AI.CONTEXT: REGIONAL_FOODS -->

### Dynamic Region Detection

**Implementation:**
1. Location-based customization
   - Client location detection
   - Automatic region setting
   - Manual override option
   - Multi-region support

2. Regional preference learning
   - Commonly used foods tracking
   - Favorite regional dishes
   - Cultural preference patterns
   - Adaptive recommendations

### Regional Database Components

**Middle Eastern Region:**
1. Staple foods
   - Falafel (طعمية مقلية)
   - Baladi bread (عيش بلدي)
   - Ful medames (فول مدمس)
   - Tabbouleh (تبولة)
   - Koshari (كشري)

2. Common preparations
   - Standard portion sizes
   - Traditional cooking methods
   - Regional variations
   - Typical combinations

**North American Region:**
1. Staple foods
   - Hamburgers and sandwiches
   - Various bread types
   - Dairy products
   - Fast food options
   - Common packaged foods

2. Measurement standards
   - Standard portion sizes
   - Imperial measurement system
   - USDA database alignment
   - Regional chain restaurant items

**European Region:**
1. Staple foods
   - Continental bread varieties
   - Regional cheese options
   - Mediterranean ingredients
   - Common prepared meals
   - Traditional dishes

2. Measurement standards
   - Metric system
   - European portion sizes
   - Regional specialties
   - Local preparation methods

**Asian Region:**
1. Staple foods
   - Rice varieties
   - Noodle options
   - Regional vegetables
   - Soy-based products
   - Common dishes by subregion

2. Measurement standards
   - Asian portion sizes
   - Regional cooking methods
   - Traditional combinations
   - Local specialties

**Latin American Region:**
1. Staple foods
   - Corn and wheat products
   - Regional bean varieties
   - Traditional dishes
   - Common preparations
   - Local specialties

2. Measurement standards
   - Latin American portion sizes
   - Regional cooking methods
   - Traditional combinations
   - Local ingredients
<!-- AI.CONTEXT.END: REGIONAL_FOODS -->

## CROSS-REGIONAL FUNCTIONALITY

<!-- AI.CONTEXT: CROSS_REGIONAL -->

### Global Food Database Access

**Implementation:**
1. Multi-region support
   - Primary region prioritization
   - Secondary region access
   - Global food search capability
   - Cross-cultural food mapping

2. Travel adaptation
   - Temporary region switching
   - Location-based updates
   - Foreign food identification
   - Nutritional equivalence mapping

### Language Support

**Implementation:**
1. Multi-language processing
   - Primary language detection
   - Secondary language support
   - Food name translation
   - Measurement conversion

2. Regional terminology
   - Local food name recognition
   - Regional measurement terms
   - Cultural preparation methods
   - Traditional combinations
<!-- AI.CONTEXT.END: CROSS_REGIONAL -->

## INTEGRATION SYSTEMS

<!-- AI.CONTEXT: INTEGRATION_SYSTEMS -->

### Training Protocol Integration

**Implementation:**
1. Workout-specific recommendations
   - Pre-workout nutrition
   - Post-workout recovery
   - Energy system support
   - Performance optimization

2. Mode-specific adjustments
   - DEFAULT MODE balance
   - WARRIOR MODE intensity support
   - DARKKNIGHT MODE precision focus
   - Recovery optimization

### Goal Framework Alignment

**Implementation:**
1. Goal-specific calculations
   - Weight management
   - Performance enhancement
   - Recovery optimization
   - Energy system support

2. Progress tracking
   - Goal alignment verification
   - Adjustment recommendations
   - Success metrics
   - Pattern optimization
<!-- AI.CONTEXT.END: INTEGRATION_SYSTEMS -->

## CUSTOMIZATION TOOLS

<!-- AI.CONTEXT: CUSTOMIZATION_TOOLS -->

### Personal Profile Integration

**Implementation:**
1. Demographic information
   - Age/sex/height/weight
   - Region/location
   - Activity level
   - Training frequency
   - Recovery capacity

2. Metabolic calculations
   - BMR estimation
   - TDEE calculation
   - Activity adjustment
   - Individual variation

### Preference Management

**Implementation:**
1. Food preferences
   - Dietary restrictions
   - Regional preferences
   - Cultural considerations
   - Preferred foods
   - Excluded items
   - Timing preferences

2. Meal structure
   - Region-specific meal patterns
   - Eating frequency
   - Portion sizes
   - Meal timing
   - Fasting protocols
<!-- AI.CONTEXT.END: CUSTOMIZATION_TOOLS -->

## EDUCATIONAL COMPONENTS

<!-- AI.CONTEXT: EDUCATIONAL_COMPONENTS -->

### Nutrition Knowledge Base

**Implementation:**
1. Macro education
   - Protein functions
   - Carbohydrate utilization
   - Fat metabolism
   - Energy balance

2. Timing principles
   - Meal frequency effects
   - Training integration
   - Recovery optimization
   - System support

### Cultural Nutrition Insights

**Implementation:**
1. Region-specific wisdom
   - Traditional eating patterns
   - Cultural nutritional practices
   - Historical dietary approaches
   - Modern adaptation strategies

2. Cross-cultural benefits
   - Global nutritional insights
   - Beneficial practices adoption
   - Cultural food diversity
   - Nutritional pattern integration
<!-- AI.CONTEXT.END: EDUCATIONAL_COMPONENTS -->

## IMPLEMENTATION GUIDELINES

<!-- AI.CONTEXT: IMPLEMENTATION_GUIDELINES -->

### Usage Protocol

**Interaction Flow:**
1. Input methods
   - Type "client:" followed by food items
   - Submit in list format (one item per line)
   - Include quantities and descriptions
   - Use native language as preferred

2. Output presentation
   - Structured meal breakdown
   - Individual item analysis
   - Meal totals
   - Remaining daily values
   - Personalized recommendations

### Regional Adaptation

**Protocol:**
1. Initial setup
   - Location detection from client info
   - Region setting confirmation
   - Primary language identification
   - Regional database activation

2. Ongoing adaptation
   - Frequently used foods tracking
   - Regional preference learning
   - Cross-regional integration as needed
   - Travel adaptation support
<!-- AI.CONTEXT.END: IMPLEMENTATION_GUIDELINES -->