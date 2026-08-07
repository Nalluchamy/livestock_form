from typing import Dict, Any, List
from backend.grading import constants


class ValidationError(Exception):
    pass


def validate_attributes(attributes: Dict[str, Any]) -> List[str]:
    """
    Validates the input attributes. Returns a list of missing required attributes.
    Raises ValidationError for invalid values.
    """
    missing = []
    for attr in constants.ALL_ATTRIBUTES:
        if attr not in attributes:
            missing.append(attr)
            continue
            
        value = attributes[attr]
        
        if attr == constants.ATTR_BODY_CONDITION:
            try:
                bcs = float(value)
                if not (1.0 <= bcs <= 5.0):
                    raise ValidationError(f"Body condition must be between 1.0 and 5.0, got {bcs}")
            except (ValueError, TypeError):
                raise ValidationError(f"Body condition must be a number, got {value}")
        
        elif attr == constants.ATTR_COAT_QUALITY and value not in constants.COAT_VALUES:
            raise ValidationError(f"Invalid coat quality: {value}. Expected one of {constants.COAT_VALUES}")
            
        elif attr == constants.ATTR_EYE_CONDITION and value not in constants.EYE_VALUES:
            raise ValidationError(f"Invalid eye condition: {value}. Expected one of {constants.EYE_VALUES}")
            
        elif attr == constants.ATTR_WOUND_PRESENCE and value not in constants.WOUND_VALUES:
            raise ValidationError(f"Invalid wound presence: {value}. Expected one of {constants.WOUND_VALUES}")
            
        elif attr == constants.ATTR_MOBILITY and value not in constants.MOBILITY_VALUES:
            raise ValidationError(f"Invalid mobility: {value}. Expected one of {constants.MOBILITY_VALUES}")
            
        elif attr == constants.ATTR_APPETITE and value not in constants.APPETITE_VALUES:
            raise ValidationError(f"Invalid appetite: {value}. Expected one of {constants.APPETITE_VALUES}")

    # Check for unknown attributes
    for attr in attributes:
        if attr not in constants.ALL_ATTRIBUTES:
            raise ValidationError(f"Unknown attribute provided: {attr}")

    return missing
