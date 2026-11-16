from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from app.models import db, Complaint, User
from app.routes.auth import admin_required

admin_bp = Blueprint("admin", __name__)

@admin_bp.before_request
@admin_required
def require_admin_auth():
    """Ensure user is logged in as an administrator."""
    pass

@admin_bp.route("/dashboard")
def dashboard():
    """Executive administrator dashboard with operational metrics and quick actions."""
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status="Pending").count()
    in_progress_complaints = Complaint.query.filter_by(status="In Progress").count()
    resolved_complaints = Complaint.query.filter_by(status="Resolved").count()
    high_priority_count = Complaint.query.filter_by(priority="High").count()
    total_students = User.query.filter_by(role="student").count()

    # Recent complaints across all users
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(8).all()

    # Status distribution for charts
    status_counts = {
        "Pending": pending_complaints,
        "In Progress": in_progress_complaints,
        "Resolved": resolved_complaints
    }

    # Category distribution
    categories_data = {}
    for cat in Complaint.CATEGORIES:
        count = Complaint.query.filter_by(category=cat).count()
        if count > 0:
            categories_data[cat] = count

    return render_template(
        "admin_dashboard.html",
        total_complaints=total_complaints,
        pending_complaints=pending_complaints,
        in_progress_complaints=in_progress_complaints,
        resolved_complaints=resolved_complaints,
        high_priority_count=high_priority_count,
        total_students=total_students,
        recent_complaints=recent_complaints,
        status_counts=status_counts,
        categories_data=categories_data,
        statuses=Complaint.STATUSES,
        priorities=Complaint.PRIORITIES,
    )

@admin_bp.route("/complaints")
def complaints_list():
    """Admin complaints management table with multi-filter and search."""
    query_str = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "").strip()
    priority_filter = request.args.get("priority", "").strip()
    category_filter = request.args.get("category", "").strip()

    base_query = Complaint.query.join(User)

    if query_str:
        pattern = f"%{query_str}%"
        base_query = base_query.filter(
            (Complaint.title.ilike(pattern)) |
            (Complaint.location.ilike(pattern)) |
            (Complaint.description.ilike(pattern)) |
            (User.name.ilike(pattern)) |
            (User.email.ilike(pattern))
        )

    if status_filter and status_filter in Complaint.STATUSES:
        base_query = base_query.filter(Complaint.status == status_filter)

    if priority_filter and priority_filter in Complaint.PRIORITIES:
        base_query = base_query.filter(Complaint.priority == priority_filter)

    if category_filter and category_filter in Complaint.CATEGORIES:
        base_query = base_query.filter(Complaint.category == category_filter)

    complaints = base_query.order_by(Complaint.created_at.desc()).all()

    return render_template(
        "admin_complaints.html",
        complaints=complaints,
        categories=Complaint.CATEGORIES,
        priorities=Complaint.PRIORITIES,
        statuses=Complaint.STATUSES,
        q=query_str,
        selected_status=status_filter,
        selected_priority=priority_filter,
        selected_category=category_filter,
    )

@admin_bp.route("/complaints/<int:complaint_id>/update", methods=["POST"])
def update_complaint(complaint_id):
    """Update the status and priority of any complaint."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        abort(404)

    new_status = request.form.get("status")
    new_priority = request.form.get("priority")

    if new_status and new_status in Complaint.STATUSES:
        complaint.status = new_status

    if new_priority and new_priority in Complaint.PRIORITIES:
        complaint.priority = new_priority

    db.session.commit()
    flash(f"Complaint #{complaint.id} successfully updated (Status: {complaint.status}, Priority: {complaint.priority}).", "success")

    # Redirect back to referring page or admin dashboard
    ref = request.referrer
    if ref and ("/admin/" in ref or "/student/" in ref):
        return redirect(ref)
    return redirect(url_for("admin.complaints_list"))

@admin_bp.route("/complaints/<int:complaint_id>/delete", methods=["POST"])
def delete_complaint(complaint_id):
    """Delete an inappropriate or duplicate complaint with admin privileges."""
    complaint = db.session.get(Complaint, complaint_id)
    if not complaint:
        abort(404)

    cid = complaint.id
    db.session.delete(complaint)
    db.session.commit()

    flash(f"Complaint #{cid} was deleted.", "info")
    return redirect(url_for("admin.complaints_list"))

@admin_bp.route("/stats/json")
def stats_json():
    """API endpoint providing real-time analytics data for dashboard charts."""
    status_data = {
        "Pending": Complaint.query.filter_by(status="Pending").count(),
        "In Progress": Complaint.query.filter_by(status="In Progress").count(),
        "Resolved": Complaint.query.filter_by(status="Resolved").count()
    }
    
    category_data = {}
    for cat in Complaint.CATEGORIES:
        category_data[cat] = Complaint.query.filter_by(category=cat).count()

    priority_data = {
        "Low": Complaint.query.filter_by(priority="Low").count(),
        "Medium": Complaint.query.filter_by(priority="Medium").count(),
        "High": Complaint.query.filter_by(priority="High").count()
    }

    return jsonify({
        "status": status_data,
        "category": category_data,
        "priority": priority_data
    })
