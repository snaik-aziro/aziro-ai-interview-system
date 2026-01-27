# src/utils/question_generator/role_config.py

"""
Single source of truth for ROLE → ROUND → QUESTION BANK mapping
DO NOT rename this file
DO NOT split logic
"""

ROLE_TO_TEST_CONFIG = {

    # =====================================================
    # ENTRY / JUNIOR ROLES (NO DOMAIN)
    # =====================================================

    "python_entry": {
        "L1": "L1_master_questions.json",
        "L2": "L2_python_master-questions.json",
        "L3": "L3_python_master_questions.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",   # ✅ Soft Skills
    },

    "java_entry": {
        "L1": "L1_master_questions.json",
        "L2": "L2_java_master_questions.json",
        "L3": "L3_java_master_questions.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",   # ✅ Soft Skills
    },

    "js_entry": {
        "L1": "L1_master_questions.json",
        "L2": "L2_js_master_questions.json",
        "L3": "L3_js_master_questions.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",   # ✅ Soft Skills
    },

    # =====================================================
    # SENIOR / QA / DEV ROLES (DOMAIN OPTIONAL)
    # =====================================================

    "python_qa_linux": {
        "L1": "L1_linux_master_questions.json",
        "L2": "L2_python_master-questions.json",
        "L3": "L3_qa_testing_5_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",   # ✅ Soft Skills (ALWAYS)
        "L6": "domain_optional",             # ✅ Domain (ONLY if selected)
    },

    "python_qa": {
        "L1": "L1_master_questions.json",
        "L2": "L2_python_master-questions.json",
        "L3": "L3_qa_testing_5_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",
        "L6": "domain_optional",
    },

    "python_dev": {
        "L1": "L1_master_questions.json",
        "L2": "L2_python_master-questions.json",
        "L3": "L3_python_dev_4_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",
        "L6": "domain_optional",
    },

    "python_ai_ml": {
        "L1": "L1_master_questions.json",
        "L2": "L2_python_master-questions.json",
        "L3": "L3_ai_ml_4_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",
        "L6": "domain_optional",
    },

    "java_aws": {
        "L1": "L1_master_questions.json",
        "L2": "L2_java_master_questions.json",
        "L3": "L3_aws_dev_5_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",
        "L6": "domain_optional",
    },

    "java_qa": {
        "L1": "L1_master_questions.json",
        "L2": "L2_java_master_questions.json",
        "L3": "L3_qa_testing_5_yrs.json",
        "L4": "coding",
        "L5": "L5_master_questions.json",
        "L6": "domain_optional",
    },
}
