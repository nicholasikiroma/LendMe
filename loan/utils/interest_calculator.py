from datetime import timedelta


def loan_cal(amount, duration, interest, start_date, end_date):
    """Calculate repayment amount"""
    # Calculate the daily interest rate
    daily_interest = interest / 30

    # Calculate the total interest based on the loan duration
    total_interest = interest * (duration // 30)

    # Calculate the additional interest if payment is made after the loan duration
    if end_date > start_date + timedelta(days=duration):
        total_interest += total_interest * 0.05

    # Calculate the number of days between start_date and end_date
    days_elapsed = (end_date - start_date).days

    # Calculate the interest accumulated if loan is paid before the duration is elapsed
    if days_elapsed < duration:
        accrued_interest = daily_interest * days_elapsed
        total_interest += accrued_interest

    # Calculate the total amount due
    amount_due = round(amount + total_interest, 2)

    return amount_due
