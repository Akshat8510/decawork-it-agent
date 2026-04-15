"""
Mock IT Admin Panel — Flask Application
Provides 3 pages/actions:
  1. /           — Dashboard overview
  2. /users       — User management (create, reset password, disable/enable)
  3. /licenses    — License management (assign, revoke)
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
import json, os

app = Flask(__name__)
app.secret_key = "it-admin-secret-2024"

# ── In-memory "database" ──────────────────────────────────────────────────────
USERS: dict[str, dict] = {
    "alice@company.com": {
        "name": "Alice Johnson",
        "email": "alice@company.com",
        "role": "Engineer",
        "status": "active",
        "license": "Microsoft 365",
        "created_at": "2024-01-10",
        "last_login": "2025-04-14",
    },
    "bob@company.com": {
        "name": "Bob Smith",
        "email": "bob@company.com",
        "role": "Designer",
        "status": "active",
        "license": None,
        "created_at": "2024-03-22",
        "last_login": "2025-04-10",
    },
}

LICENSES: dict[str, dict] = {
    "Microsoft 365": {"total": 10, "assigned": 1},
    "Slack Pro":      {"total": 20, "assigned": 0},
    "Zoom Business":  {"total": 5,  "assigned": 0},
    "GitHub Enterprise": {"total": 8, "assigned": 0},
}

AUDIT_LOG: list[dict] = []


def log_action(action: str, detail: str):
    AUDIT_LOG.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "detail": detail,
    })


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    active_users   = sum(1 for u in USERS.values() if u["status"] == "active")
    disabled_users = sum(1 for u in USERS.values() if u["status"] == "disabled")
    total_licenses = sum(v["total"]    for v in LICENSES.values())
    used_licenses  = sum(v["assigned"] for v in LICENSES.values())
    return render_template(
        "index.html",
        active_users=active_users,
        disabled_users=disabled_users,
        total_licenses=total_licenses,
        used_licenses=used_licenses,
        audit_log=AUDIT_LOG[:10],
        users=USERS,
    )


# ── User Management ───────────────────────────────────────────────────────────

@app.route("/users")
def users():
    return render_template("users.html", users=USERS, licenses=list(LICENSES.keys()))


@app.route("/users/create", methods=["POST"])
def create_user():
    name  = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    role  = request.form.get("role", "").strip()

    if not name or not email:
        flash("Name and email are required.", "error")
        return redirect(url_for("users"))
    if email in USERS:
        flash(f"User {email} already exists.", "error")
        return redirect(url_for("users"))

    USERS[email] = {
        "name": name,
        "email": email,
        "role": role or "Employee",
        "status": "active",
        "license": None,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "last_login": "Never",
    }
    log_action("CREATE_USER", f"Created user {name} <{email}>")
    flash(f"User {name} created successfully.", "success")
    return redirect(url_for("users"))


@app.route("/users/reset_password", methods=["POST"])
def reset_password():
    email = request.form.get("email", "").strip().lower()
    if email not in USERS:
        flash(f"User {email} not found.", "error")
        return redirect(url_for("users"))

    temp_pw = f"TempPass@{datetime.now().strftime('%H%M%S')}"
    log_action("RESET_PASSWORD", f"Password reset for {email}. Temp password: {temp_pw}")
    flash(f"Password for {email} reset. Temporary password: {temp_pw}", "success")
    return redirect(url_for("users"))


@app.route("/users/toggle_status", methods=["POST"])
def toggle_status():
    email = request.form.get("email", "").strip().lower()
    if email not in USERS:
        flash(f"User {email} not found.", "error")
        return redirect(url_for("users"))

    user = USERS[email]
    new_status = "disabled" if user["status"] == "active" else "active"
    user["status"] = new_status
    log_action("TOGGLE_STATUS", f"{email} set to {new_status}")
    flash(f"User {email} is now {new_status}.", "success")
    return redirect(url_for("users"))


@app.route("/users/delete", methods=["POST"])
def delete_user():
    email = request.form.get("email", "").strip().lower()
    if email not in USERS:
        flash(f"User {email} not found.", "error")
        return redirect(url_for("users"))

    user = USERS.pop(email)
    # free up any license
    if user["license"] and user["license"] in LICENSES:
        LICENSES[user["license"]]["assigned"] = max(0, LICENSES[user["license"]]["assigned"] - 1)
    log_action("DELETE_USER", f"Deleted user {email}")
    flash(f"User {email} deleted.", "success")
    return redirect(url_for("users"))


# ── License Management ────────────────────────────────────────────────────────

@app.route("/licenses")
def licenses():
    return render_template("licenses.html", licenses=LICENSES, users=USERS)


@app.route("/licenses/assign", methods=["POST"])
def assign_license():
    email   = request.form.get("email", "").strip().lower()
    license_name = request.form.get("license", "").strip()

    if email not in USERS:
        flash(f"User {email} not found.", "error")
        return redirect(url_for("licenses"))
    if license_name not in LICENSES:
        flash(f"License '{license_name}' not found.", "error")
        return redirect(url_for("licenses"))

    lic = LICENSES[license_name]
    if lic["assigned"] >= lic["total"]:
        flash(f"No available seats for {license_name}.", "error")
        return redirect(url_for("licenses"))

    # free old license first
    old_lic = USERS[email]["license"]
    if old_lic and old_lic in LICENSES:
        LICENSES[old_lic]["assigned"] = max(0, LICENSES[old_lic]["assigned"] - 1)

    USERS[email]["license"] = license_name
    lic["assigned"] += 1
    log_action("ASSIGN_LICENSE", f"Assigned {license_name} to {email}")
    flash(f"{license_name} assigned to {email}.", "success")
    return redirect(url_for("licenses"))


@app.route("/licenses/revoke", methods=["POST"])
def revoke_license():
    email = request.form.get("email", "").strip().lower()
    if email not in USERS:
        flash(f"User {email} not found.", "error")
        return redirect(url_for("licenses"))

    old_lic = USERS[email]["license"]
    if not old_lic:
        flash(f"{email} has no license to revoke.", "error")
        return redirect(url_for("licenses"))

    LICENSES[old_lic]["assigned"] = max(0, LICENSES[old_lic]["assigned"] - 1)
    USERS[email]["license"] = None
    log_action("REVOKE_LICENSE", f"Revoked {old_lic} from {email}")
    flash(f"License revoked from {email}.", "success")
    return redirect(url_for("licenses"))


# ── JSON API helpers (used by agent for state checks) ─────────────────────────

@app.route("/api/users")
def api_users():
    return jsonify(list(USERS.values()))


@app.route("/api/user/<email>")
def api_user(email):
    u = USERS.get(email.lower())
    if not u:
        return jsonify({"error": "not found"}), 404
    return jsonify(u)


@app.route("/api/licenses")
def api_licenses():
    return jsonify(LICENSES)


if __name__ == "__main__":
    app.run(debug=True, port=5000)