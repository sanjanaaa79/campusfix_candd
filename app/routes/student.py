from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from app.models import db, Complaint, User
from app.routes.auth import login_required, student_required

student_bp = Blueprint("student", __name__)

@student_bp.before_request
@login_required
def require_student_auth():
    """Ensure user is logged in before accessing student views."""
    pass

@student_bp.route("/dashboard")
def dashboard():
    """Render the student overview dashboard with metrics and recent items."""
    user_id = session.get("user_id")

    # Metrics for the current student
    total_complaints = Complaint.query.filter_by(user_id=user_id).count()
    pending_complaints = Complaint.query.filter_by(user_id=user_id, status="Pending").count()
    in_progress_complaints = Complaint.query.filter_by(user_id=user_id, status="In Progress").count()
    resolved_complaints = Complaint.query.filter_by(user_id=user_id, status="Resolved").count()

    # Recent complaints
    recent_complaints = (
        Complaint.query.filter_by(user_id=user_id)
        .order_by(Complaint.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "student_dashboard.html",
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        recent_complaints=recent_complaints,
    )

@student_bp.route("/complaints/new", methods=["GET", "POST"])
def submit_complaint():
    """Lodge a new campus maintenance complaint."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category = request.form.get("category", "").strip()
        location = request.form.get("location", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium").strip()

        # Validation
        if not title or not category or not location or not description:
            flash("Please complete all required fields.", "danger")
            return render_template(
                "submit_complaint.html",
                categories=Complaint.CATEGORIES,
                priorities=Complaint.PRIORITIES,
                title=title,
                category=category,
                location=location,
                description=description,
                priority=priority,
            )

        if category not in Complaint.CATEGORIES:
            flash("Invalid category selected.", "danger")
            return render_template(
                "submit_complaint.html",
                categories=Complaint.CATEGORIES,
                priorities=Complaint.PRIORITIES,
            )

        if priority not in Complaint.PRIORITIES:
            priority = "Medium"

        complaint = Complaint(
            user_id=session["user_id"],
            title=title,
            category=category,
            location=location,
            description=description,
            priority=priority,
            status="Pending"
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f"Complaint #{complaint.id} registered successfully! Campus staff will review it shortly.", "success")
        return redirect(url_for("student.my_complaints"))

    return render_template(
        "submit_complaint.html",
        categories=Complaint.CATEGORIES,
        priorities=Complaint.PRIORITIES,
    )

@student_bp.route("/complaints")
def my_complaints():
    """List all complaints submitted by the current student with filtering & search."""
    user_id = session.get("user_id")

    query_str = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    category_filter = request.args.get("category", "").strip()

    base_query = Complaint.query.filter_by(user_id=user_id)

    if query_str:
        search_pattern = f"%{query_str}%"
        base_query = base_query.filter(
            (Complaint.title.ilike(search_pattern)) |
            (Complaint.location.ilike(search_pattern)) |
            (Complaint.description.ilike(search_pattern))
        )

    if status_filter and status_filter in Complaint.STATUSES:
        base_query = base_query.filter_by(status=status_filter)

    if category_filter and category_filter in Complaint.CATEGORIES:
        base_query = base_query.filter_by(category=category_filter)

    complaints = base_query.order_by(Complaint.created_at.desc()).all()

    return render_template(
        "my_complaints.html",
        complaints=complaints,
        categories=Complaint.CATEGORIES,
        statuses=Complaint.STATUSES,
        q=query_str,
        selected_status=status_filter,
        selected_category=category_filter,
    )

@student_bp.route("/complaints/<int:complaint_id>")
def complaint_detail(complaint_id):
    """View detailed information and status log for a specific complaint."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        abort(404)

    # Authorization check: Student can only view their own complaint
    user_id = session.get("user_id")
    user_role = session.get("user_role")

    if user_role != "admin" and complaint.user_id != user_id:
        abort(403)

    return render_template("complaint_detail.html", complaint=complaint)
