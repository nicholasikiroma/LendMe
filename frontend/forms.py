from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import (
    EmailField,
    PasswordField,
    StringField,
    IntegerField,
    HiddenField,
    SelectField,
    DecimalField,
)
from wtforms.validators import InputRequired, equal_to, NumberRange, Optional


class LoginForm(FlaskForm):
    """Fields for login form"""

    email = EmailField(
        label="Email", validators=[InputRequired(message="Enter a valid email address")]
    )
    password = PasswordField(
        label="Password", validators=[InputRequired(message="Password cannot be blank")]
    )


class SignUpForm(FlaskForm):
    """Fields for sign up form"""

    first_name = StringField(
        label="First Name", validators=[InputRequired(message="Field cannot be blank")]
    )
    last_name = StringField(
        label="Last Name", validators=[InputRequired(message="Field cannot be blank")]
    )
    email = EmailField(
        label="Email", validators=[InputRequired(message="Enter a valid email address")]
    )
    password = PasswordField(
        label="Password", validators=[InputRequired(message="Password cannot be blank")]
    )
    confirm_password = PasswordField(
        label="Confirm Password",
        validators=[
            InputRequired(message="Password cannot be blank"),
            equal_to("password", message="Passwords do not match"),
        ],
    )


def validate_loan_term(form, field):
    if field.data % 30 != 0:
        raise ValidationErr("Loan term duration must be multiples of 30 days.")


class LoanForm(FlaskForm):
    amount = IntegerField(
        label="Loan Amount", validators=[InputRequired(message="Enter loan amount.")]
    )
    interest = IntegerField(
        label="Interest (%)",
        validators=[
            NumberRange(
                min=1, max=5, message="Interest should be within the range of 1 and 5"
            )
        ],
    )
    duration = IntegerField(
        label="Duration (days)",
        validators=[
            InputRequired(message="Timeframe for loan repayment"),
            validate_loan_term,
        ],
    )
    lender_id = HiddenField(validators=[InputRequired(message="Lender ID not found")])


class FinancialProfileForm(FlaskForm):
    credit_score = IntegerField(
        label="Credit score",
        validators=[InputRequired(message="Field cannot be left blank")],
    )
    monthly_income = IntegerField(
        label="Credit score",
        validators=[InputRequired(message="Field cannot be left blank")],
    )
    debt_payments = IntegerField(
        label="Debt Repayments (optional)", validators=[Optional()]
    )
    employment_status = SelectField(
        label="Employment status", choices=["EMPLOYED", "SELF-EMPLOYED", "UNEMPLOYED"]
    )



class FundWalletForm(FlaskForm):
    amount = IntegerField(label="Amount", validators=[InputRequired(message="Amount cannot be left blank")])


class TransactionForm(FlaskForm):
    narration = StringField(label="Transaction Narration", validators=[InputRequired(message="Provide narration for this transaction")])
    sender_id = StringField(label="Sender ID", validators=[InputRequired(message="Wallet cannot be left blank")])
    receiver_id = StringField(label="Receiver ID", validators=[InputRequired(message="Wallet cannot be left blank")])
    amount = DecimalField(label="Amount", validators=[InputRequired(message="Provide amount")])
