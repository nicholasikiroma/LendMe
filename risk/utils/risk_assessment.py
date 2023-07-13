"""Module contains logic for risk assessment"""
def generate_report_summary(result):
    is_eligible = result["is_eligible"]
    risk_score = result["risk_score"]
    debt_to_income_ratio = result["debt_to_income_ratio"]

    # Generate a sentence-like summary based on the assessment result
    summary = "Loan Assessment Report:\n\n"
    
    if is_eligible:
        summary += "The user is eligible for this loan. "
    else:
        summary += "The user is not eligible for this loan. "
    
    summary += "They have a risk score of {} which shows their capacity to repay the loan, ".format(risk_score)
    summary += "and a DTI ratio of {}.".format(debt_to_income_ratio)

    return summary



def risk_assessment(loan_amount, borrower_profile):
    """
        Args:
            loan_amount(int) - amount to be borrowed
            borrower_profile(JSON) - financial profile of user
        Returns:
            result(DICT)
    """
    # Extract relevant information from the borrower profile
    monthly_income = borrower_profile["monthly_income"]
    debt_payments = borrower_profile.get("debt_payments")
    employment_status = borrower_profile["employment_status"]
    credit_score = borrower_profile["credit_score"]
    is_defaulter = borrower_profile["is_defaulter"]

    # Calculate the debt-to-income ratio
    if debt_payments is not None:
        debt_to_income_ratio = debt_payments / monthly_income
    else:
        debt_to_income_ratio = 0

    # Assess the borrower's risk score based on various factors
    risk_score = 0

    # Check if the borrower has a high debt-to-income ratio
    if debt_to_income_ratio > 0.4:
        risk_score += 0.5

    # Adjust the risk score based on employment status
    if employment_status == "UNEMPLOYED":
        risk_score += 0.7
    elif employment_status == "SELF_EMPLOYED":
        risk_score += 0.3

    # Adjust the risk score based on credit score and defaulter status
    if credit_score < 600:
        risk_score += 0.6
    if is_defaulter:
        risk_score += 0.8

    # Determine loan eligibility based on risk score and loan amount
    is_eligible = risk_score < 1.5 and loan_amount <= 100000

    # Prepare the result dictionary
    result = {
        "is_eligible": is_eligible,
        "risk_score": risk_score,
        "debt_to_income_ratio": debt_to_income_ratio
    }

    return result
