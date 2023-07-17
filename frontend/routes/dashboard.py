from datetime import date
from flask import Blueprint, render_template, session, flash, redirect, request, url_for
from api.wallet_service import WalletClient
from api.loan_service import LoanClient
from api.risk_service import RiskClient
from api.user_service import UserClient
from routes.auth import login_required
from forms import LoanForm, FinancialProfileForm, FundWalletForm, TransactionForm


blp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard",
    template_folder="../templates/dashboard",
)


@blp.route("/")
@login_required
def dashboard():
    """Render dashboard"""
    current_user = session["current_user"]
    wallet = WalletClient.get_wallet(current_user["wallet_id"])

    user_loans = LoanClient.get_user_loans(current_user["id"])
    user_applications = LoanClient.get_user_applications(current_user["id"])

    investments = None
    liabilities = None

    if isinstance(user_loans, dict):
        loan_error = user_loans["error"]
        flash(loan_error)

    else:
        investments = len(user_loans)

    if isinstance(user_applications, dict):
        app_error = user_applications["error"]
        flash(app_error)

    else:
        liabilities = len(user_applications)

    return render_template(
        "dashboard.html",
        user=current_user,
        wallet=wallet,
        investments=investments,
        liabilities=liabilities,
    )


# start of loan operations
@blp.route("/loans/explore")
def discover_loans():
    """View all open loans"""
    loans = LoanClient.get_all_loans()

    if isinstance(loans, dict):
        flash(loans["error"])
        return render_template("loans.html", loans=None)

    return render_template("loans.html", loans=loans)


@blp.route("/loans/new", methods=["POST", "GET"])
@login_required
def create_loan():
    """Create a new loan listing"""

    lender_id = None
    current_user = session.get("current_user", None)
    if current_user:
        lender_id = current_user["id"]
    else:
        flash("You are not authenticated")
        return redirect(url_for("user_auth.login"))

    form = LoanForm(data={"lender_id": lender_id})

    if request.method == "POST" and form.validate_on_submit():
        response = LoanClient.create_loan(form)
        loan_id = response.get("id", None)
        if loan_id:
            flash("Loan created successfully!")
            return redirect(url_for("dashboard.discover_loans"))

        else:
            flash(response["error"])

    return render_template("create_loan.html", form=form, lender_id=lender_id)


@blp.route("/loans/my-loans")
@login_required
def my_loans():
    """View loans associated with current user"""
    user_id = session.get("current_user", {}).get("id")

    if not user_id:
        flash("Login to access resource")
        return redirect(url_for("user_auth.login"))

    user_loans = LoanClient.get_user_loans(user_id)
    user_applications = LoanClient.get_user_applications(user_id)

    if isinstance(user_loans, dict):
        loan_error = user_loans["error"]
        flash(loan_error)
        user_loans = None

    if isinstance(user_applications, dict):
        app_error = user_applications["error"]
        flash(app_error)
        user_applications = None

    return render_template(
        "userloans.html", loans=user_loans, applications=user_applications
    )


@blp.route("/loans/apply", methods=["POST"])
def submit_apply():
    """Apply to loan"""
    loan_id = request.form.get("loanId")
    lender_id = request.form.get("lenderId")
    borrower_id = session["current_user"]["id"]

    risk_profile = RiskClient.get_finance_profile(borrower_id)

    profile = risk_profile.get("id", None)

    if profile:
        application = LoanClient.apply_to_loan(
            lender_id=lender_id, borrower_id=borrower_id, loan_id=loan_id
        )
        success_msg = application.get("message", None)
        if success_msg:
            flash(success_msg)
            return redirect(url_for("dashboard.my_loans"))

        else:
            flash(application["error"])
            return redirect(url_for("dashboard.discover_loans"))

    elif risk_profile["status_code"] == 404:
        flash("Kindly update your financial profile to apply.")

    else:
        flash(risk_profile["error"])

    return redirect(url_for("dashboard.discover_loans"))


@blp.route("/loans/<uuid:loan_id>/applications")
def view_applications(loan_id):
    """Fetch all loan applications"""
    user_id = session.get("current_user", {}).get("id")
    if user_id:
        response = LoanClient.fetch_loan(loan_id)

        get_lender_id = response.get("lender_id")
        if get_lender_id:
            if response["applications"]:
                return render_template(
                    "applications.html", applications=response["applications"]
                )
            return render_template("applications.html", applications=None)
        else:
            flash(response["error"])
            return render_template("applications.html", applications=None)

    else:
        return redirect(url_for("user_auth.login"))


@blp.route("/loans/<uuid:loan_id>/application/<uuid:application_id>/accept")
@login_required
def accept_application(loan_id, application_id):
    """Accept Loan"""
    response = LoanClient.accept_application(application_id)

    if response["message"]:
        flash(response["message"])
        return redirect(url_for("dashboard.disburse_loan", loan_id=loan_id))

    elif response["error"]:
        flash(response["error"])
        return redirect(url_for("dashboard.my_loans"))


@blp.route("/loans/<uuid:loan_id>/disburse")
@login_required
def disburse_loan(loan_id):
    """Start payment process"""
    start_date = date.today()
    start_loan = LoanClient.update_start_date(start_date, loan_id)

    lender_id = start_loan.get("lender_id", None)
    if lender_id:
        payment_details = {
            "amount_due": start_loan["amount"],
            "sender_id": start_loan["lender_id"],
            "receiver_id": start_loan["borrower_id"],
        }
        session["payment_details"] = payment_details
        return redirect(url_for("dashboard.transfer_funds"))
    else:
        flash(start_loan["error"])
        return redirect(url_for("dashboard.my_loans"))


@blp.route("/loans/<uuid:loan_id>/repayments")
@login_required
def repay_details(loan_id):
    """Start repayment process"""
    end_date = date.today()
    end_loan = LoanClient.update_end_date(end_date, loan_id)

    lender_id = end_loan.get("lender_id", None)
    if lender_id:
        repayment_details = LoanClient.get_repayment_details(loan_id)
        loan = repayment_details.get("loan_id", None)
        if loan:
            payment_details = {
                "sender_id": repayment_details["borrower_id"],
                "receiver_id": repayment_details["lender_id"],
                "amount_due": repayment_details["amount_due"],
            }

            session["payment_details"] = payment_details
            return render_template("repayment.html", context=repayment_details)
        else:
            flash(repayment_details["error"])
            return render_template("repayment.html", context=None)
    else:
        flash(end_loan["error"])
        return redirect(url_for("dashboard.my_loans"))


# End of loan operations


# Risk operations
@blp.route("/financial-profile", methods=["POST", "GET"])
@login_required
def update_profile():
    """Update financial details for user"""
    profile = None
    user_id = session.get("current_user", {}).get("id")

    if user_id:
        response = RiskClient.get_finance_profile(user_id)
        profile = response.get("id", None)
        if profile:
            finance_profile = response
            return render_template("profile.html", profile=finance_profile)

        elif response["status_code"] == 404:
            form = FinancialProfileForm()
            if request.method == "POST" and form.validate_on_submit():
                client_response = RiskClient.create_finance_profile(form)

                profile = client_response.get("id", None)
                if profile:
                    flash("Profile updated successfully!")
                    return redirect(url_for("dashboard.dashboard"))

                else:
                    flash(response["error"])
                    return redirect(url_for("dashboard.update_profile"))

            return render_template("profile.html", profile=profile)

        else:
            flash(response["error"])
            return render_template("profile.html")

    else:
        flash("You need to be logged in")
        return redirect(url_for("user_auth.login"))


@blp.route("/<uuid:borrower_id>/profile")
@login_required
def get_profile(borrower_id):
    """Fetch financial profile"""

    response = RiskClient.get_finance_profile(borrower_id)
    profile = response.get("id", None)
    if profile:
        return render_template("finance_profile.html", profile=response)
    else:
        flash(response["error"])
        return render_template("finance_profile.html")


@blp.route("/<uuid:loan_id>/report/<uuid:borrower_id>")
@login_required
def generate_assessment_report(borrower_id, loan_id):
    """Fetch financial profile"""

    response = RiskClient.fetch_finance_report(borrower_id)
    report = response.get("id", None)
    if report:
        return render_template("report.html", report=response)
    else:
        loan = LoanClient.fetch_loan(loan_id)

        loan_amount = loan.get("amount", None)
        if loan_amount:
            new_report = RiskClient.create_finance_report(
                borrower_id, loan_amount, loan_id
            )
            report_id = new_report.get("id", None)
            if report_id:
                return render_template("report.html", report=new_report)
            else:
                flash(new_report["error"])
                return render_template("report.html")
        else:
            flash(loan["error"])
            return render_template("report.html")


# end risk operations


# wallet operations
@blp.route("/fund-wallet", methods=["GET", "POST"])
@login_required
def fund_wallet():
    """View function for funding wallet"""
    form = FundWalletForm()
    if request.method == "POST" and form.validate_on_submit():
        wallet_id = session["current_user"]["wallet_id"]
        amount = form.amount.data

        response = WalletClient.fund_wallet(wallet_id, amount)

        fund = response.get("id", None)
        if fund:
            flash("You've succesfully funded your account!")
            return redirect(url_for("dashboard.dashboard"))

        else:
            flash(response["error"])

    return render_template("fund_wallet.html", form=form)


@blp.route("/wallet/transaction-history", methods=["GET"])
@login_required
def transaction_history():
    """Fetch transaction history for user"""
    user = session.get("current_user", {})
    if user:
        wallet_id = user["wallet_id"]
        response = WalletClient.get_wallet(wallet_id)

        wallet = response.get("id", None)
        if wallet:
            if response["transactions"]:
                return render_template(
                    "transactions.html", transactions=response["transactions"]
                )
            else:
                return render_template("transactions.html", transactions=None)

        else:
            flash(response["error"])
            return render_template("transactions.html", transactions=None)

    else:
        return redirect(url_for("user_auth.login"))


@blp.route("/wallet/transfer", methods=["POST", "GET"])
@login_required
def transfer_funds():
    """Transfer funds from one wallet to another"""
    transaction_details = session.get("payment_details", None)

    if transaction_details:
        amount = transaction_details["amount_due"]
        sender_id = transaction_details["sender_id"]
        receiver_id = transaction_details["receiver_id"]

        form = TransactionForm(
            data={
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "amount": float(amount),
            }
        )

        if request.method == "POST" and form.validate_on_submit():
            transaction = WalletClient.create_transaction(form)
            response = transaction.get("reference_id", None)
            if response:
                flash("Transfer Successful!")
                return redirect(url_for("dashboard.dashboard"))
            else:
                flash(transaction["error"])
                return render_template("payment.html", form=form)
        else:
            return render_template("payment.html", form=form)
    else:
        flash("Transaction details not found!")
        return redirect(url_for("dashboard.my_loans"))


# end wallet operations
