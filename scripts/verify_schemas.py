import sys
import os

# Add src to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(os.path.join(project_root, "src"))

try:
    from tax_parser.schemas import ScheduleK1Partnership, ScheduleK1SCorp
    from tax_parser.models.result import FormType
    from tax_parser.schemas import get_schema_for_form
    
    print("Successfully imported ScheduleK1Partnership and ScheduleK1SCorp")
    
    # Test instantiating Partnership K-1
    k1_1065 = ScheduleK1Partnership()
    print(f"Created instance of 1065: {k1_1065.form_type}")
    
    # Test instantiating S-Corp K-1
    k1_1120s = ScheduleK1SCorp()
    print(f"Created instance of 1120-S: {k1_1120s.form_type}")
    
    # Test registry
    reg_1065 = get_schema_for_form(FormType.SCHEDULE_K1_PARTNERSHIP)
    print(f"Registry lookup for 1065: {reg_1065}")
    assert reg_1065 == ScheduleK1Partnership
    
    reg_1120s = get_schema_for_form(FormType.SCHEDULE_K1_SCORP)
    print(f"Registry lookup for 1120-S: {reg_1120s}")
    assert reg_1120s == ScheduleK1SCorp

    # Test partner type assignment
    k1_1065.partner.partner_type = "individual"
    print(f"Partner type set: {k1_1065.partner.partner_type}")

    # Test numeric field
    k1_1120s.income_deductions.line_1_ordinary_business_income = 1250.50
    print(f"Income set: {k1_1120s.income_deductions.line_1_ordinary_business_income}")

    print("\nAll basic verification tests passed!")

except Exception as e:
    print(f"Verification failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
